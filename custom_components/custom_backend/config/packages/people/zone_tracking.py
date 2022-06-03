"Tracking people as they move around zones"

from json import dumps, loads
from logging import getLogger
from math import cos, asin, sqrt, pi
from typing import Optional

from homeassistant.core import HomeAssistant, State

from custom_components.custom_backend.const import (
	ATTR_GPS_ACCURACY,
	ATTR_LATITUDE,
	ATTR_LONGITUDE,
	BROWSER_MOBILE_APP,
	CHANNEL_LOCATION_UPDATES,
	CONF_ENTITIES,
	CONF_ENTITY_ID,
	CONF_ICON,
	CONF_INCLUDE,
	CONF_MAX,
	CONF_NAME,
	CONF_OPTION,
	CONF_OPTIONS,
	CONF_VALUE,
	DATA_BROWSERS,
	DATA_CAUSE,
	DATA_CHANNEL,
	DATA_COORDINATES,
	DATA_FULL_NAME,
	DATA_IMAGE,
	DATA_LATITUDE,
	DATA_LONGITUDE,
	DATA_MAP,
	DATA_MESSAGE,
	DATA_NICKNAME,
	DATA_OSES,
	DATA_PEOPLE,
	DATA_PERSON,
	DATA_PHONES,
	DATA_PHOTO,
	DATA_RADIUS,
	DATA_SLUG,
	DATA_TEXT,
	DATA_TITLE,
	DATA_ZONE,
	DATA_ZONES,
	DOMAIN_DEVICE_TRACKER,
	DOMAIN_INPUT_SELECT,
	DOMAIN_INPUT_TEXT,
	DOMAIN_PERSON,
	DOMAIN_RECORDER,
	EVENT_TYPE_HOMEASSISTANT_START,
	ICON_MDI_MAP_MARKER_CIRCLE,
	ICON_MDI_TARGET_ACCOUNT,
	IMAGE_PLACE_MARKER_COLOR,
	SERVICE_SELECT_OPTION,
	SERVICE_SET_VALUE,
)
from custom_components.custom_backend.utils import entity_state_to_readable_store, window
from custom_components.custom_backend.config.packages.notify import notify
from custom_components.custom_backend.config.packages.phones import get_phones


OPTION_DIVIDER = "―――――――――――――"
OPTION_NOT_IN_ZONE = "Not in a zone"
OPTION_SOMEWHERE_BUT_NOT_BAKA_S_HOUSE = "Could be anywhere but Baka's House"
OPTION_UNTRACKABLE = "Cannot be tracked"


_LOGGER = getLogger(__name__)


def filter_to_people_who_can_be_gps_tracked(people, phones):
	return {
		person_slug: person_data for person_slug, person_data in people.items() if any(BROWSER_MOBILE_APP in os_data[DATA_BROWSERS] for phone_slug in person_data[DATA_PHONES] for os_data in phones[phone_slug][DATA_OSES].values())
	}


async def generate_yaml(**kwds):
	people = kwds[DATA_PEOPLE]
	zones = kwds[DATA_ZONES]

	phones = await get_phones(**kwds)

	unique_zones = {zone_data[DATA_FULL_NAME] for zone_data in zones.values()}
	zone_options = [OPTION_UNTRACKABLE, OPTION_SOMEWHERE_BUT_NOT_BAKA_S_HOUSE, OPTION_NOT_IN_ZONE, OPTION_DIVIDER, *sorted(unique_zones)]
	zone_input_selects = {
		f"{person_slug}_{DATA_ZONE}": {
			CONF_ICON: ICON_MDI_MAP_MARKER_CIRCLE,
			CONF_NAME: f"{person_data[DATA_FULL_NAME]}'s Zone",
			CONF_OPTIONS: zone_options,
		} for person_slug, person_data in people.items()
	}

	people_who_can_be_gps_tracked = filter_to_people_who_can_be_gps_tracked(people, phones)
	coordinates_input_texts = {
		f"{person_slug}_{DATA_COORDINATES}": {
			CONF_ICON: ICON_MDI_TARGET_ACCOUNT,
			CONF_MAX: 255,
			CONF_NAME: f"{person_data[DATA_FULL_NAME]}'s GPS Coordinates",
		} for person_slug, person_data in people_who_can_be_gps_tracked.items()
	}

	return {
		DOMAIN_INPUT_SELECT: {
			**zone_input_selects,
		},
		DOMAIN_INPUT_TEXT: {
			**coordinates_input_texts,
		},
		DOMAIN_RECORDER: {
			CONF_INCLUDE: {
				CONF_ENTITIES: [
					*[f"{DOMAIN_INPUT_SELECT}.{zone_input_select_slug}" for zone_input_select_slug in zone_input_selects],
					*[f"{DOMAIN_PERSON}.{person_slug}" for person_slug in people],
				]
			}
		}
	}


# https://stackoverflow.com/a/21623206/3399373
RAD_PER_DEGREE = pi/180
def distance_between_coordinates(*, lat1, lon1, lat2, lon2):
	a = 0.5 - cos((lat2-lat1)*RAD_PER_DEGREE)/2 + cos(lat1*RAD_PER_DEGREE) * cos(lat2*RAD_PER_DEGREE) * (1-cos((lon2-lon1)*RAD_PER_DEGREE))/2
	return 12742 * asin(sqrt(a)) * 1000


async def async_setup(hass: HomeAssistant, config: dict, **kwds) -> bool:
	people = kwds[DATA_PEOPLE]
	zones = kwds[DATA_ZONES]
	phones = await get_phones(**kwds)

	people_who_can_be_gps_tracked = filter_to_people_who_can_be_gps_tracked(people, phones)

	async def mobile_app_device_tracker_changed(to_state: Optional[State], *, person_slug):
		latitude = to_state.attributes[ATTR_LATITUDE]
		longitude = to_state.attributes[ATTR_LONGITUDE]
		radius_of_uncertainty = to_state.attributes[ATTR_GPS_ACCURACY]

		stringified = dumps({
			DATA_LATITUDE: latitude,
			DATA_LONGITUDE: longitude,
			DATA_RADIUS: radius_of_uncertainty,
		})

		await hass.services.async_call(DOMAIN_INPUT_TEXT, SERVICE_SET_VALUE, {
			CONF_ENTITY_ID: f"{DOMAIN_INPUT_TEXT}.{person_slug}_{DATA_COORDINATES}",
			CONF_VALUE: stringified,
		}, blocking=True)
	
	
	async def new_coordinates(new_coordinates_stringified, *, person_slug):
		parsed = loads(new_coordinates_stringified)

		latitude = parsed[DATA_LATITUDE]
		longitude = parsed[DATA_LONGITUDE]
		radius_of_uncertainty = parsed[DATA_RADIUS]

		distance_from_device_tracker_to_each_zone = {}

		# TODO
		...

		current_zone_full_name = hass.states.get(f"{DOMAIN_INPUT_SELECT}.{person_slug}_{DATA_ZONE}").state

		person_is_possibly_within = []
		person_is_definitely_within = []

		person_is_possibly_within_current = []
		
		for zone_slug, zone_data in zones.items():
			distance_from_device_tracker_to_zone = distance_between_coordinates(lat1=latitude, lon1=longitude, lat2=zone_data[DATA_LATITUDE], lon2=zone_data[DATA_LONGITUDE])
			distance_from_device_tracker_to_each_zone[zone_slug] = distance_from_device_tracker_to_zone

			# Two circles do not intersect if the distance between their centers is greater than the sum of their radii
			if distance_from_device_tracker_to_zone > (zone_data[DATA_RADIUS] + radius_of_uncertainty):
				continue
			
			person_is_possibly_within.append(zone_slug)
			if zone_data[DATA_FULL_NAME] == current_zone_full_name:
				person_is_possibly_within_current.append(zone_slug)

			# If the circle of uncertainty fits entirely within the zone's circle, then they are definitely in that zone
			if (distance_from_device_tracker_to_zone + radius_of_uncertainty) > zone_data[DATA_RADIUS]:
				continue

			person_is_definitely_within.append(zone_slug)
		
		if person_is_definitely_within:
			person_is_definitely_within.sort(key=lambda zone_slug: (distance_from_device_tracker_to_each_zone[zone_slug], zones[zone_slug][DATA_RADIUS]))
			closest_zone_definitely_containing_person = person_is_definitely_within[0]

			# As long as it's possible they're still in their current zone, don't mark them as being in a different one
			# Unless the new zone is smaller
			# For example, Baka's house vs neighborhood
			if (not person_is_possibly_within_current) or all(zones[closest_zone_definitely_containing_person][DATA_RADIUS] < zones[zone_slug][DATA_RADIUS] for zone_slug in person_is_possibly_within_current):
				await hass.services.async_call(DOMAIN_INPUT_SELECT, SERVICE_SELECT_OPTION, {
					CONF_ENTITY_ID: f"{DOMAIN_INPUT_SELECT}.{person_slug}_{DATA_ZONE}",
					CONF_OPTION: zones[closest_zone_definitely_containing_person][DATA_FULL_NAME],
				}, blocking=True)
		elif person_is_possibly_within:
			if not person_is_possibly_within_current:
				await hass.services.async_call(DOMAIN_INPUT_SELECT, SERVICE_SELECT_OPTION, {
					CONF_ENTITY_ID: f"{DOMAIN_INPUT_SELECT}.{person_slug}_{DATA_ZONE}",
					CONF_OPTION: OPTION_NOT_IN_ZONE,
				}, blocking=True)
		else:
			await hass.services.async_call(DOMAIN_INPUT_SELECT, SERVICE_SELECT_OPTION, {
				CONF_ENTITY_ID: f"{DOMAIN_INPUT_SELECT}.{person_slug}_{DATA_ZONE}",
				CONF_OPTION: OPTION_NOT_IN_ZONE,
			}, blocking=True)

	async def zone_changed(from_state: Optional[State], to_state: Optional[State], *, person_slug):
		if from_state is None:
			return
		
		if to_state is None:
			return
		
		old_zone = from_state.state
		new_zone = to_state.state

		# TODO: create a store util for filtering non-changes
		if new_zone == old_zone:
			return
		
		if new_zone == OPTION_UNTRACKABLE:
			return
		
		# TODO: skip notification if they just unlocked a lock
		
		notify_args = {
			DATA_CAUSE: {
				DATA_PERSON: person_slug,
			},
			DATA_CHANNEL: CHANNEL_LOCATION_UPDATES,
		}
		
		image = IMAGE_PLACE_MARKER_COLOR

		person_data = people[person_slug]
		if new_zone in {OPTION_NOT_IN_ZONE, OPTION_SOMEWHERE_BUT_NOT_BAKA_S_HOUSE}:
			notify_args[DATA_TEXT] = {
				DATA_TITLE: f"Left {old_zone}",
				DATA_MESSAGE: f"{person_data[DATA_NICKNAME]} left {old_zone}",
			}

			for zone_data in zones.values():
				if zone_data[DATA_FULL_NAME] == old_zone:
					this_zone_image = zone_data[DATA_IMAGE]
					if this_zone_image is not None:
						image = this_zone_image
						break
		elif old_zone in {OPTION_NOT_IN_ZONE, OPTION_SOMEWHERE_BUT_NOT_BAKA_S_HOUSE, OPTION_UNTRACKABLE}:
			notify_args[DATA_TEXT] = {
				DATA_TITLE: f"Arrived at {new_zone}",
				DATA_MESSAGE: f"{person_data[DATA_NICKNAME]} arrived at {new_zone}",
			}

			for zone_data in zones.values():
				if zone_data[DATA_FULL_NAME] == new_zone:
					this_zone_image = zone_data[DATA_IMAGE]
					if this_zone_image is not None:
						image = this_zone_image
						break
		else:
			possibly_in_old_zone = False
			new_zones_data = [zone_data for zone_data in zones.values() if zone_data[DATA_FULL_NAME] == new_zone]
			for zone_data in zones.values():
				if zone_data[DATA_FULL_NAME] != old_zone:
					continue
				for new_zone_data in new_zones_data:
					distance_from_this_zone_to_old_zone = distance_between_coordinates(lat1=new_zone_data[DATA_LATITUDE], lon1=new_zone_data[DATA_LONGITUDE], lat2=zone_data[DATA_LATITUDE], lon2=zone_data[DATA_LONGITUDE])
					sum_of_radii = new_zone_data[DATA_RADIUS] + zone_data[DATA_RADIUS]

					if sum_of_radii > distance_from_this_zone_to_old_zone:
						possibly_in_old_zone = True
						break

			notify_args[DATA_TEXT] = {
				DATA_TITLE: f"Arrived at {new_zone}",
			}

			if possibly_in_old_zone:
				notify_args[DATA_TEXT][DATA_MESSAGE] = f"{person_data[DATA_NICKNAME]} arrived at {new_zone}"
			else:
				notify_args[DATA_TEXT][DATA_MESSAGE] = f"{person_data[DATA_NICKNAME]} left {old_zone} and arrived at {new_zone}"

			for zone_data in zones.values():
				if zone_data[DATA_FULL_NAME] == new_zone:
					this_zone_image = zone_data[DATA_IMAGE]
					if this_zone_image is not None:
						image = this_zone_image
						break

		notify_args[DATA_IMAGE] = image
		
		coordinates = {}
		if person_slug in people_who_can_be_gps_tracked:
			person_coordinates_state = hass.states.get(f"{DOMAIN_INPUT_TEXT}.{person_slug}_{DATA_COORDINATES}").state
			coordinates = loads(person_coordinates_state)
		
		if coordinates:
			# todo: check if coordinates are possibly within the zone
			coordinates_possibly_within_zone = True
			if coordinates_possibly_within_zone:
				notify_args[DATA_MAP] = {
					DATA_LATITUDE: coordinates[DATA_LATITUDE],
					DATA_LONGITUDE: coordinates[DATA_LONGITUDE],
				}
			else:
				# TODO
				_LOGGER.error("Todo!")
		else:
			# TODO
			_LOGGER.error("Todo!")
			# if coordinates not available then use the coordinates of the zone

		await notify(notify_args, hass=hass, **kwds)
	
	
	async def setup_automations(event):
		for person_slug, person_data in people.items():
			[get_zone_change, subscribe_to_zone_changes] = window(entity_state_to_readable_store(f"{DOMAIN_INPUT_SELECT}.{person_slug}_{DATA_ZONE}", hass=hass))
			subscribe_to_zone_changes(lambda *, get_zone_change=get_zone_change, person_slug=person_slug: hass.async_create_task(zone_changed(*get_zone_change(), person_slug=person_slug)))

			if person_slug in people_who_can_be_gps_tracked:
				[get_coordinates, subscribe_to_coordinates] = entity_state_to_readable_store(f"{DOMAIN_INPUT_TEXT}.{person_slug}_{DATA_COORDINATES}", hass=hass)
				subscribe_to_coordinates(lambda *, get_coordinates=get_coordinates, person_slug=person_slug: hass.async_create_task(new_coordinates(get_coordinates().state, person_slug=person_slug)))
			
			for phone_slug in person_data[DATA_PHONES]:
				phone_data = phones[phone_slug]
				for os_data in phone_data[DATA_OSES].values():
					mobile_app_data = os_data[DATA_BROWSERS].get(BROWSER_MOBILE_APP)
					if mobile_app_data is None:
						continue
					
					mobile_app_slug = mobile_app_data[DATA_SLUG]

					[get_mobile_app_device_tracker_state, subscribe_to_mobile_app_device_tracker_state] = entity_state_to_readable_store(f"{DOMAIN_DEVICE_TRACKER}.{mobile_app_slug}", hass=hass)
					subscribe_to_mobile_app_device_tracker_state(lambda *, get_mobile_app_device_tracker_state=get_mobile_app_device_tracker_state, person_slug=person_slug: hass.async_create_task(mobile_app_device_tracker_changed(get_mobile_app_device_tracker_state(), person_slug=person_slug)))


	hass.bus.async_listen(EVENT_TYPE_HOMEASSISTANT_START, setup_automations)
	return True

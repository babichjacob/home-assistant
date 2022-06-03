"Notify about events from the calendar"

from datetime import datetime
from enum import Enum
from logging import getLogger

from homeassistant import core
from homeassistant.helpers.condition import time
from homeassistant.helpers.event import async_track_time_change

from custom_components.custom_backend.const import CHANNEL_TIMED_ANNOUNCEMENTS, DATA_ACTIONS, DATA_CHANNEL, DATA_CLOSE_GARAGE_DOOR, DATA_DEVICES, DATA_ID, DATA_IMAGE, DATA_MESSAGE, DATA_OPEN_GARAGE_DOOR, DATA_PEOPLE, DATA_ROOM_WITH_FREE_ACCESS, DATA_ROOM_WITH_LIMITED_ACCESS, DATA_TEXT, DATA_TITLE, DATA_UNLOCK_LOCK, DEVICE_TYPE_SPEAKER, IMAGE_CLOUDS_COLOR, IMAGE_DOG_BOWL_COLOR, IMAGE_FOG_COLOR, IMAGE_MOON_PHASE_COLOR, IMAGE_NIGHT_COLOR, IMAGE_PARTLY_CLOUDY_DAY_COLOR, IMAGE_PILL_BOTTLE_COLOR, IMAGE_RAINFALL_COLOR, IMAGE_RECYCLE_COLOR, IMAGE_SLEET_COLOR, IMAGE_SNOW_COLOR, IMAGE_SUN_COLOR, IMAGE_THERMOMETER_COLOR, IMAGE_WINDY_WEATHER_COLOR, PERSON_JACOB, ROOM_GARAGE, STATE_CLEAR_DAY, STATE_CLEAR_NIGHT, STATE_CLOUDY, STATE_FOG, STATE_PARTLY_CLOUDY_DAY, STATE_PARTLY_CLOUDY_NIGHT, STATE_PARTLYCLOUDY, STATE_RAIN, STATE_RAINY, STATE_SLEET, STATE_SNOWY, STATE_SUNNY, STATE_WIND, STATE_WINDY, TIME_FORMAT_WEEKDAY
from custom_components.custom_backend.utils import entity_state_to_readable_store
from custom_components.custom_backend.config.packages.garage_doors import get_garage_doors
from custom_components.custom_backend.config.packages.locks import get_locks
from custom_components.custom_backend.config.packages.notify import notify


_LOGGER = getLogger(__name__)


class Hourstone(Enum):
	AM_9 = 9
	PM_12 = 12
	PM_3 = 12+3
	PM_6 = 12+6
	PM_9 = 12+9

ANNOUNCEMENT_NAMES = {
	Hourstone.AM_9: "Morning Announcement",
	Hourstone.PM_12: "Noon Announcement",
	Hourstone.PM_3: "Afternoon Announcement",
	Hourstone.PM_6: "Evening Announcement",
	Hourstone.PM_9: "Night Announcement",
}
INTROS = {
	Hourstone.AM_9: "Good morning everyone!",
	Hourstone.PM_12: "It's 12 o'clock.",
	Hourstone.PM_3: "Good afternoon!",
	Hourstone.PM_6: "Good evening!",
	Hourstone.PM_9: "Good night everyone!",
}
WEATHER_IMAGES = {
	STATE_CLEAR_DAY: IMAGE_SUN_COLOR,
	STATE_CLEAR_NIGHT: IMAGE_MOON_PHASE_COLOR,
	STATE_CLOUDY: IMAGE_CLOUDS_COLOR,
	STATE_FOG: IMAGE_FOG_COLOR,
	STATE_PARTLY_CLOUDY_DAY: IMAGE_PARTLY_CLOUDY_DAY_COLOR,
	STATE_PARTLYCLOUDY: IMAGE_PARTLY_CLOUDY_DAY_COLOR,
	STATE_PARTLY_CLOUDY_NIGHT: IMAGE_NIGHT_COLOR,
	STATE_RAIN: IMAGE_RAINFALL_COLOR,
	STATE_RAINY: IMAGE_RAINFALL_COLOR,
	STATE_SLEET: IMAGE_SLEET_COLOR,
	STATE_SNOWY: IMAGE_SNOW_COLOR,
	STATE_SUNNY: IMAGE_SUN_COLOR,
	STATE_WIND: IMAGE_WINDY_WEATHER_COLOR,
	STATE_WINDY: IMAGE_WINDY_WEATHER_COLOR,
}

# TODO: replace with calendar events

async def async_setup(hass: core.HomeAssistant, config: dict, **kwds) -> bool:
	locks = await get_locks(**kwds)
	garage_doors = await get_garage_doors(**kwds)

	# TODO: WIP
	kdet_daynight = entity_state_to_readable_store("weather.kdet_daynight", hass=hass)

	async def notify_for_hourstone(hourstone: Hourstone):
		_LOGGER.error(f"sending {hourstone} announcement")

		right_now = datetime.now()
		weekday = right_now.strftime(TIME_FORMAT_WEEKDAY)

		announcement_name = ANNOUNCEMENT_NAMES[hourstone]
		intro = INTROS[hourstone]

		title = f"{weekday} {announcement_name}"

		message = intro

		condition = None

		kdet_daynight_state = kdet_daynight[0]()


		if hourstone == Hourstone.PM_9:
			_LOGGER.error(f"it's 9 pm")

			ATTR_FORECAST = "forecast" # TODO
			forecasts = kdet_daynight_state.attributes[ATTR_FORECAST]
			tomorrow_day_forecast = forecasts[1]
			# TODO: check daytime key

			DATA_DETAILED_DESCRIPTION = "detailed_description" # TODO

			tomorrow_s_weather_summary = f"Tomorrow's weather will be {tomorrow_day_forecast[DATA_DETAILED_DESCRIPTION]}"

			DATA_CONDITION = "condition" # TODO
			condition = tomorrow_day_forecast[DATA_CONDITION]

			# tomorrow_s_weather_summary = f"Tomorrow's weather will be {tomorrow_summary}"

			# tomorrow_s_weather_apparent_high = f" but it'll feel as hot as {tomorrow_temperature_high_apparent}{tomorrow_temperature_high_apparent_unit}"
			# tomorrow_s_weather_apparent_low = f" but it'll feel as cold as {tomorrow_temperature_low_apparent}{tomorrow_temperature_low_apparent_unit}"
			# tomorrow_s_weather_high_and_low = f"The high will be {tomorrow_temperature_high}{tomorrow_temperature_high_unit}{tomorrow_s_weather_apparent_high if tomorrow_temperature_high != tomorrow_temperature_high_apparent else ""}, and the low will be {tomorrow_temperature_low}{tomorrow_temperature_low_unit}{tomorrow_s_weather_apparent_low if tomorrow_temperature_low != tomorrow_temperature_low_apparent else ""}."
			# tomorrow_s_weather_precipitation = f"There'll be a {tomorrow_precipitation_probability}% chance of {tomorrow_precipitation_type}."

			# tomorrow_s_weather = f"{tomorrow_s_weather_summary}\n\n{tomorrow_s_weather_high_and_low}\n\n{tomorrow_s_weather_precipitation}"

			message += f" {tomorrow_s_weather_summary}"
		else:
			_LOGGER.error(f"it's any other time of day than 9 pm")

			condition = kdet_daynight_state.state
			...

		image = WEATHER_IMAGES.get(condition, IMAGE_THERMOMETER_COLOR)

		await notify({
			DATA_CHANNEL: CHANNEL_TIMED_ANNOUNCEMENTS,
			DATA_IMAGE: image,
			DATA_TEXT: {
				DATA_TITLE: title,
				DATA_MESSAGE: message,
			},
		}, hass=hass, **kwds)

	async def hourstone_9_am(point_in_time):
		"""At 9 am: send a morning announcement"""
		await notify_for_hourstone(Hourstone.AM_9)
	async_track_time_change(hass, hourstone_9_am, hour=Hourstone.AM_9.value, minute=00, second=00)

	async def hourstone_12_pm(point_in_time):
		"""At 12 pm: send a noon announcement"""
		await notify_for_hourstone(Hourstone.PM_12)
	async_track_time_change(hass, hourstone_12_pm, hour=Hourstone.PM_12.value, minute=00, second=00)

	async def hourstone_3_pm(point_in_time):
		"""At 3 pm: send an afternoon announcement"""
		await notify_for_hourstone(Hourstone.PM_3)
	async_track_time_change(hass, hourstone_3_pm, hour=Hourstone.PM_3.value, minute=00, second=00)

	async def hourstone_6_pm(point_in_time):
		"""At 6 pm: send an evening announcement"""
		await notify_for_hourstone(Hourstone.PM_6)
	async_track_time_change(hass, hourstone_6_pm, hour=Hourstone.PM_6.value, minute=00, second=00)

	async def hourstone_9_pm(point_in_time):
		"""At 9 pm: send a night announcement"""
		await notify_for_hourstone(Hourstone.PM_9)
	async_track_time_change(hass, hourstone_9_pm, hour=Hourstone.PM_9.value, minute=00, second=00)


	async def notify_to_feed_lola(point_in_time):
		"""At 7 pm every day: inform people they need to feed Lola"""
		await notify({
			DATA_IMAGE: IMAGE_DOG_BOWL_COLOR,
			DATA_TEXT: {
				DATA_TITLE: "Feed the Dog",
				DATA_MESSAGE: "It's time to feed Lola dinner!",
			},
		}, hass=hass, **kwds)
	async_track_time_change(hass, notify_to_feed_lola, hour=12+7, minute=00, second=00)


	async def notify_to_fill_cat_s_water_bowl(point_in_time):
		"""At 7 pm every day: inform Jacob to refill the cats' water bowl"""
		await notify({
			DATA_IMAGE: IMAGE_DOG_BOWL_COLOR,
			DATA_PEOPLE: [PERSON_JACOB],
			DATA_TEXT: {
				DATA_TITLE: "Refill the Cats' Water Bowl",
				DATA_MESSAGE: "It's time to refill the cats' water bowl!",
			},
		}, hass=hass, **kwds)
	async_track_time_change(hass, notify_to_fill_cat_s_water_bowl, hour=0, minute=30, second=00)


	async def notify_for_wheel_of_fortune():
		await notify({
			DATA_DEVICES: [DEVICE_TYPE_SPEAKER],
			DATA_TEXT: {
				DATA_TITLE: "Wheel of Fortune",
				DATA_MESSAGE: "It's almost time for Wheel of Fortune! It'll be on in just a couple of minutes.",
			},
		}, hass=hass, **kwds)

	async def weekday_wheel_of_fortune_notification(point_in_time):
		"""At 6:57 pm on weekdays: inform people that Wheel of Fortune is coming on"""

		if time(weekday=["mon", "tue", "wed", "thu", "fri"], hass=hass):
			await notify_for_wheel_of_fortune()
	async_track_time_change(hass, weekday_wheel_of_fortune_notification, hour=12+6, minute=57, second=00)

	async def saturday_wheel_of_fortune_notification(point_in_time):
		"""At 7:27 pm on Saturdays: inform people that Wheel of Fortune is coming on"""

		if time(weekday=["sat"], hass=hass):
			await notify_for_wheel_of_fortune()
	async_track_time_change(hass, saturday_wheel_of_fortune_notification, hour=12+7, minute=27, second=00)

	async def take_out_trash_and_recycling_notification(point_in_time):
		"""At 6:03 pm on Sundays: tell people to take out the trash and recycling"""

		if time(weekday=["sun"], hass=hass):
			room_trash_and_recycling_is_in = ROOM_GARAGE
			garage_doors_matching = [garage_door_slug for garage_door_slug, garage_door_data in garage_doors.items() if garage_door_data[DATA_ROOM_WITH_FREE_ACCESS] == room_trash_and_recycling_is_in]
			locks_matching = [lock_slug for lock_slug, lock_data in locks.items() if lock_data[DATA_ROOM_WITH_LIMITED_ACCESS] == room_trash_and_recycling_is_in]

			actions = []
			for garage_door_slug in garage_doors_matching:
				actions.append({
					DATA_ID: f"{DATA_OPEN_GARAGE_DOOR}_{garage_door_slug}",
				})
				actions.append({
					DATA_ID: f"{DATA_CLOSE_GARAGE_DOOR}_{garage_door_slug}",
				})
			
			for lock_slug in locks_matching:
				actions.append({
					DATA_ID: f"{DATA_UNLOCK_LOCK}_{lock_slug}",
				})

			await notify({
				DATA_ACTIONS: actions,
				DATA_IMAGE: IMAGE_RECYCLE_COLOR,
				DATA_TEXT: {
					DATA_TITLE: "Trash and Recycling",
					DATA_MESSAGE: "It's time to take out the trash and recycling!",
				},
			}, hass=hass, **kwds)
	async_track_time_change(hass, take_out_trash_and_recycling_notification, hour=12+6, minute=3, second=00)

	async def jacob_multivitamin_notification(point_in_time):
		"""At 1:35 pm: tell Jacob to take their multivitamin"""

		await notify({
			DATA_IMAGE: IMAGE_PILL_BOTTLE_COLOR,
			DATA_PEOPLE: [PERSON_JACOB],
			DATA_TEXT: {
				DATA_TITLE: "Daily Multivitamin",
				DATA_MESSAGE: "It's time to take your daily multivitamin!",
			},
		}, hass=hass, **kwds)
	async_track_time_change(hass, jacob_multivitamin_notification, hour=12+1, minute=40, second=00)

	async def jacob_vitamin_d3_pill_notification(point_in_time):
		"""At 1:40 pm on Sundays: tell Jacob to take their Vitamin D3 pill"""

		if time(weekday=["sun"], hass=hass):
			await notify({
				DATA_IMAGE: IMAGE_PILL_BOTTLE_COLOR,
				DATA_PEOPLE: [PERSON_JACOB],
				DATA_TEXT: {
					DATA_TITLE: "Vitamin D3 Pill",
					DATA_MESSAGE: "It's time to take your weekly vitamin D3 pill!",
				},
			}, hass=hass, **kwds)
	async_track_time_change(hass, jacob_vitamin_d3_pill_notification, hour=12+1, minute=40, second=00)

	return True

"Notify about the garage doors"

from logging import getLogger

from homeassistant import core
from homeassistant.helpers.event import async_track_state_change

from custom_components.custom_backend.const import CHANNEL_GARAGE_DOOR_ACTIVITY, DATA_ACTIONS, DATA_CAMERA, DATA_CHANNEL, DATA_CLOSE_GARAGE_DOOR, DATA_FULL_NAME, DATA_GROUP, DATA_ID, DATA_IMAGE, DATA_MESSAGE, DATA_ROOM, DATA_ROOM_WITH_FREE_ACCESS, DATA_ROOM_WITH_LIMITED_ACCESS, DATA_SHORT_NAME, DATA_TEXT, DATA_TITLE, DOMAIN_COVER, EVENT_TYPE_HOMEASSISTANT_START, IMAGE_GARAGE_DOOR_CLOSED_COLOR, IMAGE_GARAGE_DOOR_OPEN_COLOR, STATE_CLOSED, STATE_CLOSING, STATE_OPEN, STATE_OPENING
from custom_components.custom_backend.config.packages.cameras import get_cameras
from custom_components.custom_backend.config.packages.notify import notify

from . import get_garage_doors


_LOGGER = getLogger(__name__)



async def async_setup(hass: core.HomeAssistant, config: dict, **kwds) -> bool:
	cameras = await get_cameras(**kwds)
	garage_doors = await get_garage_doors(**kwds)

	# TODO: personalized garage_door entities like the locks
	async def garage_door_state_changed(*, garage_door_slug, previous_state, new_state):
		garage_door_data = garage_doors[garage_door_slug]
		cameras_in_the_free_access_room = [camera_slug for camera_slug, camera_data in cameras.items() if camera_data[DATA_ROOM] == garage_door_data[DATA_ROOM_WITH_FREE_ACCESS]]
		cameras_in_the_limited_access_room = [camera_slug for camera_slug, camera_data in cameras.items() if camera_data[DATA_ROOM] == garage_door_data[DATA_ROOM_WITH_LIMITED_ACCESS]]
		# TODO: in_view like the locks

		notify_args = {}

		if previous_state in {STATE_CLOSED, STATE_CLOSING} and new_state in {STATE_OPEN, STATE_OPENING}:
			notify_args = {
				DATA_ACTIONS: [
					{
						DATA_ID: f"{DATA_CLOSE_GARAGE_DOOR}_{garage_door_slug}",
					}
				],
				DATA_CHANNEL: CHANNEL_GARAGE_DOOR_ACTIVITY,
				DATA_GROUP: f"{garage_door_data[DATA_FULL_NAME]} Activity",
				DATA_IMAGE: IMAGE_GARAGE_DOOR_OPEN_COLOR,
				DATA_TEXT: {
					DATA_MESSAGE: f"The {garage_door_data[DATA_FULL_NAME].lower()} has been opened!",
					DATA_TITLE: f"{garage_door_data[DATA_FULL_NAME]} Opened",
				},
			}

			cameras_showing_the_action = [*cameras_in_the_free_access_room, *cameras_in_the_limited_access_room]
			if cameras_showing_the_action:
				notify_args[DATA_CAMERA] = cameras_showing_the_action[0]
		elif previous_state in {STATE_OPEN, STATE_OPENING} and new_state in {STATE_CLOSED, STATE_CLOSING}:
			notify_args = {
				DATA_CHANNEL: CHANNEL_GARAGE_DOOR_ACTIVITY,
				DATA_GROUP: f"{garage_door_data[DATA_FULL_NAME]} Activity",
				DATA_IMAGE: IMAGE_GARAGE_DOOR_CLOSED_COLOR,
				DATA_TEXT: {
					DATA_MESSAGE: f"The {garage_door_data[DATA_FULL_NAME].lower()} has been closed!",
					DATA_TITLE: f"{garage_door_data[DATA_FULL_NAME]} Closed",
				},
			}

			cameras_showing_the_action = [*cameras_in_the_free_access_room, *cameras_in_the_limited_access_room]
			if cameras_showing_the_action:
				notify_args[DATA_CAMERA] = cameras_showing_the_action[0]
		
		if notify_args:
			await notify(notify_args, hass=hass, **kwds)

	async def setup_automations(event):
		for garage_door_slug in garage_doors:
			async_track_state_change(hass=hass, entity_ids=[f"{DOMAIN_COVER}.{garage_door_slug}"], action=lambda entity_id, from_state, to_state, *, garage_door_slug=garage_door_slug: hass.async_create_task(garage_door_state_changed(garage_door_slug=garage_door_slug, previous_state=from_state.state, new_state=to_state.state)))


	hass.bus.async_listen(EVENT_TYPE_HOMEASSISTANT_START, setup_automations)
	
	return True

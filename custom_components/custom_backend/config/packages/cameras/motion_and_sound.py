"Reacting to motion and sound events reported by the cameras"

from datetime import datetime
from logging import getLogger

from parse import parse

from homeassistant.core import HomeAssistant

from custom_components.custom_backend.const import (
	CHANNEL_CAMERA_ACTIVITY,
	CONF_DATETIME,
	CONF_ENTITY_ID,
	CONF_HAS_DATE,
	CONF_HAS_TIME,
	CONF_ICON,
	CONF_NAME,
	DATA_AUDIO,
	DATA_CAMERA,
	DATA_CHANNEL,
	DATA_COLOR,
	DATA_EVENT_NAME,
	DATA_FULL_NAME,
	DATA_GROUP,
	DATA_IMAGE,
	DATA_IS_OUTSIDE,
	DATA_MESSAGE,
	DATA_MOTION_DETECTED,
	DATA_NICKNAME,
	DATA_PEOPLE,
	DATA_PUSH,
	DATA_ROOM,
	DATA_ROOMS,
	DATA_TEXT,
	DATA_TITLE,
	DATA_TRIGGER_TIME,
	DATA_TTS,
	DATA_WYZE,
	DOMAIN_CAMERA,
	DOMAIN_INPUT_DATETIME,
	EVENT_TYPE_HOMEASSISTANT_START,
	EVENT_TYPE_IFTTT_WEBHOOK_RECEIVED,
	ICON_MDI_MOTION_SENSOR,
	IMAGE_MOTION_DETECTOR_COLOR,
	NOTIFICATION_COLOR_PINK,
	PERSON_JACOB,
	PUSH_SOUND_NFC_SCAN_COMPLETE,
	SERVICE_SET_DATETIME,
	TIME_FORMAT_INPUT_DATETIME,
	TIME_FORMAT_PRETTY_DATE_AT_TIME,
)
from custom_components.custom_backend.utils import entity_state_to_readable_store, window

from custom_components.custom_backend.config.packages.notify import notify

from . import get_cameras


_LOGGER = getLogger(__name__)

async def generate_yaml(**kwds):
	cameras = await get_cameras(**kwds)

	create_wyze_camera_motion_event_input_datetimes = {
		f"{camera_slug}_{DATA_WYZE}_{DATA_MOTION_DETECTED}": {
			CONF_HAS_DATE: True,
			CONF_HAS_TIME: True,
			CONF_ICON: ICON_MDI_MOTION_SENSOR,
			CONF_NAME: f"{camera_data[DATA_FULL_NAME]}'s Last Motion Event (as reported by Wyze)",
		} for camera_slug, camera_data in cameras.items()
	}

	create_camera_motion_event_input_datetimes = {
		f"{camera_slug}_{DATA_MOTION_DETECTED}": {
			CONF_HAS_DATE: True,
			CONF_HAS_TIME: True,
			CONF_ICON: ICON_MDI_MOTION_SENSOR,
			CONF_NAME: f"{camera_data[DATA_FULL_NAME]}'s Last Motion Event",
		} for camera_slug, camera_data in cameras.items()
	}

	return {
		DOMAIN_INPUT_DATETIME: {
			**create_wyze_camera_motion_event_input_datetimes,
			**create_camera_motion_event_input_datetimes,
		}
	}


async def async_setup(hass: HomeAssistant, config: dict, **kwds) -> bool:
	rooms = kwds[DATA_ROOMS]

	cameras = await get_cameras(**kwds)

	camera_nickname_to_slug = {camera_data[DATA_NICKNAME]: camera_slug for camera_slug, camera_data in cameras.items()}

	camera_wyze_motion_event_stores = {}
	camera_motion_event_stores = {}

	async def ifttt_webhook_received(event):
		if event.data[DATA_EVENT_NAME] == "wyze_motion":
			camera_nickname = parse("Motion detected on {}", event.data[DATA_MOTION_DETECTED])[0]
			motion_event_datetime = datetime.strptime(event.data[DATA_TRIGGER_TIME], TIME_FORMAT_PRETTY_DATE_AT_TIME)
			camera_slug = camera_nickname_to_slug[camera_nickname]

			[get_last_motion_event, _subscribe_to_last_motion_event] = camera_wyze_motion_event_stores[camera_slug]

			last_motion_event_datetime = datetime.strptime(get_last_motion_event().state, TIME_FORMAT_INPUT_DATETIME)

			if motion_event_datetime >= last_motion_event_datetime:
				await hass.services.async_call(DOMAIN_INPUT_DATETIME, SERVICE_SET_DATETIME, {
					CONF_DATETIME: motion_event_datetime.strftime(TIME_FORMAT_INPUT_DATETIME),
					CONF_ENTITY_ID: f"{DOMAIN_INPUT_DATETIME}.{camera_slug}_{DATA_WYZE}_{DATA_MOTION_DETECTED}",
				}, blocking=True)
			else:
				_LOGGER.warning(f"somehow, this wyze camera motion event ({motion_event_datetime} on {camera_nickname}) is further in the past than the last one ({last_motion_event_datetime})?!?!")

	async def setup_ifttt_webhooks(event):
		hass.bus.async_listen(EVENT_TYPE_IFTTT_WEBHOOK_RECEIVED, ifttt_webhook_received)
	
	hass.bus.async_listen(EVENT_TYPE_HOMEASSISTANT_START, setup_ifttt_webhooks)

	async def update_main_motion_event_from_wyze(*, camera_slug):
		[get_last_wyze_motion_event, _subscribe_to_last_wyze_motion_event] = camera_wyze_motion_event_stores[camera_slug]
		motion_event_datetime = datetime.strptime(get_last_wyze_motion_event().state, TIME_FORMAT_INPUT_DATETIME)

		[get_last_motion_event, _subscribe_to_last_motion_event] = camera_motion_event_stores[camera_slug]

		last_motion_event_datetime = datetime.strptime(get_last_motion_event().state, TIME_FORMAT_INPUT_DATETIME)

		if motion_event_datetime >= last_motion_event_datetime:
			await hass.services.async_call(DOMAIN_INPUT_DATETIME, SERVICE_SET_DATETIME, {
				CONF_DATETIME: motion_event_datetime.strftime(TIME_FORMAT_INPUT_DATETIME),
				CONF_ENTITY_ID: f"{DOMAIN_INPUT_DATETIME}.{camera_slug}_{DATA_MOTION_DETECTED}",
			}, blocking=True)
		else:
			_LOGGER.warning(f"somehow, this wyze camera motion event ({motion_event_datetime} on {DOMAIN_CAMERA}.{camera_slug}) is further in the past than the last one ({last_motion_event_datetime})?!?!")

	async def scan_or_notify(*, camera_slug):
		"Scan for objects detected in the camera, or notify if TensorFlow isn't available"

		camera_data = cameras[camera_slug]

		try:
			raise NotImplementedError("TensorFlow isn't set up yet")
		except:
			room_name = camera_data[DATA_ROOM]
			room_data = rooms[room_name]

			# TODO
			if room_data[DATA_IS_OUTSIDE]:
				await notify({
					# TODO: actions
					DATA_AUDIO: {
						DATA_PUSH: PUSH_SOUND_NFC_SCAN_COMPLETE,
						DATA_TTS: f"Motion in the {room_name.lower()}!",
					},
					DATA_CAMERA: camera_slug,
					DATA_CHANNEL: CHANNEL_CAMERA_ACTIVITY,
					DATA_COLOR: NOTIFICATION_COLOR_PINK,
					DATA_GROUP: "Household Activity",
					DATA_IMAGE: IMAGE_MOTION_DETECTOR_COLOR,
					DATA_PEOPLE: [PERSON_JACOB], # TODO: staging
					DATA_TEXT: {
						DATA_MESSAGE: f"There was motion detected in the {room_name.lower()}!",
						DATA_TITLE: f"Motion in the {room_name}",
					},
				}, **kwds, hass=hass)
		else:
			# TODO
			...

	for camera_slug in cameras:
		last_wyze_motion_event_store = entity_state_to_readable_store(f"{DOMAIN_INPUT_DATETIME}.{camera_slug}_{DATA_WYZE}_{DATA_MOTION_DETECTED}", hass=hass)
		camera_wyze_motion_event_stores[camera_slug] = last_wyze_motion_event_store

		[_get_wyze_motion_event_changes, subscribe_to_wyze_motion_event_changes] = window(last_wyze_motion_event_store, 2)
		subscribe_to_wyze_motion_event_changes(lambda *, camera_slug=camera_slug: hass.async_create_task(scan_or_notify(camera_slug=camera_slug)))

		last_motion_event_store = entity_state_to_readable_store(f"{DOMAIN_INPUT_DATETIME}.{camera_slug}_{DATA_MOTION_DETECTED}", hass=hass)
		camera_motion_event_stores[camera_slug] = last_motion_event_store

		[_get_motion_event_changes, subscribe_to_motion_event_changes] = window(last_motion_event_store, 2)
		subscribe_to_motion_event_changes(lambda *, camera_slug=camera_slug: hass.async_create_task(update_main_motion_event_from_wyze(camera_slug=camera_slug)))

	return True

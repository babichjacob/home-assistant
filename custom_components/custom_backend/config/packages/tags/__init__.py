"Registered all the RFID tags with the home automation and security system"

from asyncio import gather, sleep
from datetime import datetime
from logging import getLogger
from custom_components.custom_backend.config.packages.notify.mobile_app import (
	notify_mobile_app,
)
from custom_components.custom_backend.config.packages.people.zone_tracking import (
	OPTION_UNTRACKABLE,
)

from custom_components.custom_backend.const import (
	BROWSER_MOBILE_APP,
	CHANNEL_LOCK_ACTIVITY,
	CONF_ENTITY_ID,
	CONF_OPTION,
	DATA_ACTION,
	DATA_ACTIONS,
	DATA_AUDIO,
	DATA_BLINDS,
	DATA_BROWSERS,
	DATA_CAMERA,
	DATA_CAUSE,
	DATA_CHANNEL,
	DATA_CLOSE_GARAGE_DOOR,
	DATA_COLOR,
	DATA_DATETIME,
	DATA_DEVICE_ID,
	DATA_FULL_NAME,
	DATA_ID,
	DATA_IMAGE,
	DATA_IN_VIEW,
	DATA_LOCKS,
	DATA_MESSAGE,
	DATA_NICKNAME,
	DATA_OSES,
	DATA_PERSON,
	DATA_PHONES,
	DATA_PUSH,
	DATA_ROOM,
	DATA_ROOM_WITH_FREE_ACCESS,
	DATA_ROOM_WITH_LIMITED_ACCESS,
	DATA_SLUG,
	DATA_TAG_ID,
	DATA_TEXT,
	DATA_TITLE,
	DATA_ZONE,
	DOMAIN_COVER,
	DOMAIN_CUSTOM_BACKEND,
	DOMAIN_INPUT_SELECT,
	DOMAIN_LOCK,
	IMAGE_CURTAIN_COLOR,
	IMAGE_LOCK_UNLOCKED_COLOR,
	IMAGE_WINDOW_SHADE_COLOR,
	LOCK_DOOR_TO_THE_GARAGE,
	LOCK_FRONT_DOOR,
	NOTIFICATION_COLOR_GREEN,
	PRIORITY_EMERGENCY,
	PUSH_SOUND_AUTOUNLOCK_HAPTIC,
	ROOM_JACOB_S_BEDROOM,
	SERVICE_CLOSE_COVER,
	SERVICE_OPEN_COVER,
	SERVICE_SELECT_OPTION,
	SERVICE_UNLOCK,
	SHARED_MEMORY_REMOTE_UNLOCKING,
	STATE_CLOSED,
	WINDOW_JACOB_S_BEDROOM,
	ZONE_BAKA_S_HOUSE,
)
from custom_components.custom_backend.utils import entity_state_to_readable_store

from custom_components.custom_backend.config.packages.cameras import get_cameras
from custom_components.custom_backend.config.packages.garage_doors import (
	get_garage_doors,
)
from custom_components.custom_backend.config.packages.locks import get_locks
from custom_components.custom_backend.config.packages.notify import notify
from custom_components.custom_backend.config.packages.people import get_people
from custom_components.custom_backend.config.packages.phones import get_phones
from custom_components.custom_backend.config.packages.windows import get_windows


_LOGGER = getLogger(__name__)


def find_slug_of_device(device_id, phones):
	for phone_slug, phone_data in phones.items():
		for os_data in phone_data[DATA_OSES].values():
			mobile_app_data = os_data[DATA_BROWSERS].get(BROWSER_MOBILE_APP)

			if mobile_app_data is not None:
				if mobile_app_data[DATA_DEVICE_ID] == device_id:
					return phone_slug


def find_owner_of_slug(phone_slug, people):
	for person_slug, person_data in people.items():
		if phone_slug in person_data[DATA_PHONES]:
			return person_slug


def find_owner_of_device(device_id, people, phones):
	phone_slug = find_slug_of_device(device_id, phones)
	return find_owner_of_slug(phone_slug, people)


def toggle_blinds(window_slug, *, people, phones, windows, kwds):
	blinds_entity_id = f"{DOMAIN_COVER}.{window_slug}_{DATA_BLINDS}"
	blinds_data = windows[window_slug][DATA_BLINDS]

	async def toggle_these_blinds(*, event, hass, tag_data):
		device_id = event.data[DATA_DEVICE_ID]

		phone_slug = find_slug_of_device(device_id, phones)
		person_slug = find_owner_of_slug(phone_slug, people)

		phone_data = phones[phone_slug]

		blinds_state_store = entity_state_to_readable_store(blinds_entity_id, hass=hass)
		blinds_state = blinds_state_store[0]().state

		if blinds_state == STATE_CLOSED:
			opening = True
			toggle_task = hass.services.async_call(
				DOMAIN_COVER,
				SERVICE_OPEN_COVER,
				{
					CONF_ENTITY_ID: blinds_entity_id,
				},
				blocking=True,
			)
		else:
			opening = False
			toggle_task = hass.services.async_call(
				DOMAIN_COVER,
				SERVICE_CLOSE_COVER,
				{
					CONF_ENTITY_ID: blinds_entity_id,
				},
				blocking=True,
			)

		# TODO: these should affect the scanning device and the "device is accompanying person" smart detector thing should use that to update the person's location
		zone_input_select_entity_id = f"{DOMAIN_INPUT_SELECT}.{person_slug}_{DATA_ZONE}"
		mark_at_zone_task = hass.services.async_call(
			DOMAIN_INPUT_SELECT,
			SERVICE_SELECT_OPTION,
			{
				CONF_ENTITY_ID: zone_input_select_entity_id,
				CONF_OPTION: tag_data[DATA_ZONE],
			},
			blocking=True,
		)

		room_input_select_entity_id = f"{DOMAIN_INPUT_SELECT}.{person_slug}_{DATA_ROOM}"
		mark_in_room_task = hass.services.async_call(
			DOMAIN_INPUT_SELECT,
			SERVICE_SELECT_OPTION,
			{
				CONF_ENTITY_ID: room_input_select_entity_id,
				CONF_OPTION: tag_data[DATA_ROOM],
			},
			blocking=True,
		)

		same_device_notify_tasks = []
		for os, os_data in phone_data[DATA_OSES].items():
			mobile_app_data = os_data[DATA_BROWSERS].get(BROWSER_MOBILE_APP)

			if mobile_app_data is None:
				continue

			title = "Opening Blinds" if opening else "Closing Blinds"
			message = (
				f"{blinds_data[DATA_FULL_NAME]} are being opened now!"
				if opening
				else f"{blinds_data[DATA_FULL_NAME]} are being closed now!"
			)
			image = IMAGE_CURTAIN_COLOR if opening else IMAGE_WINDOW_SHADE_COLOR

			same_device_notify_tasks.append(
				notify_mobile_app(
					actions=None,
					camera=None,
					channel=None,
					color=None,
					group=None,
					image=image,
					map=None,
					message=message,
					message_html=message,
					os=os,
					priority=PRIORITY_EMERGENCY,  # TODO: not really an emergency but should be TTS
					push_sound=None,
					replace=None,
					slug=mobile_app_data[DATA_SLUG],
					subtitle=None,
					title=title,
					title_html=title,
					tts=message,
					use_speaker=True,
					hass=hass,
				)
			)

		await gather(
			*same_device_notify_tasks, toggle_task, mark_at_zone_task, mark_in_room_task
		)

	return toggle_these_blinds


def unlock_a_lock(lock_slug, *, cameras, garage_doors, locks, people, phones, kwds):
	async def unlock_this_lock(*, event, hass, tag_data):
		device_id = event.data[DATA_DEVICE_ID]

		phone_slug = find_slug_of_device(device_id, phones)
		person_slug = find_owner_of_slug(phone_slug, people)

		phone_data = phones[phone_slug]

		if person_slug is None:
			_LOGGER.error(f"rejecting unmatched device {device_id}")
			return

		_LOGGER.error(
			f"hi {person_slug} scanning {event.data[DATA_TAG_ID]} from {device_id}"
		)

		person_data = people[person_slug]

		# TODO: insane levels of copy-pasteitis...

		hass.data[DOMAIN_CUSTOM_BACKEND][SHARED_MEMORY_REMOTE_UNLOCKING][lock_slug] = {
			DATA_DATETIME: datetime.now(),
			DATA_PERSON: person_slug,
		}

		lock_data = locks[lock_slug]

		notify_args = {
			DATA_AUDIO: {
				DATA_PUSH: PUSH_SOUND_AUTOUNLOCK_HAPTIC,
			},
			DATA_CAUSE: {
				DATA_PERSON: person_slug,
			},
			DATA_CHANNEL: CHANNEL_LOCK_ACTIVITY,
			DATA_COLOR: NOTIFICATION_COLOR_GREEN,
			DATA_IMAGE: IMAGE_LOCK_UNLOCKED_COLOR,
			DATA_TEXT: {
				DATA_MESSAGE: f"{person_data[DATA_NICKNAME]} unlocked the {lock_data[DATA_NICKNAME].lower()} by scanning!",
				DATA_TITLE: f"{lock_data[DATA_NICKNAME]} Unlocked",
			},
		}

		notify_task = notify(notify_args, hass=hass, **kwds)

		unlock_task = hass.services.async_call(
			DOMAIN_LOCK,
			SERVICE_UNLOCK,
			{
				CONF_ENTITY_ID: f"{DOMAIN_LOCK}.{lock_slug}",
			},
			blocking=True,
		)

		this_lock_s_rooms = {
			lock_data[DATA_ROOM_WITH_FREE_ACCESS],
			lock_data[DATA_ROOM_WITH_LIMITED_ACCESS],
		}
		matching_garage_doors = [
			garage_door_slug
			for garage_door_slug, garage_door_data in garage_doors.items()
			if garage_door_data[DATA_ROOM_WITH_FREE_ACCESS] in this_lock_s_rooms
			or garage_door_data[DATA_ROOM_WITH_LIMITED_ACCESS] in this_lock_s_rooms
		]

		cameras_in_the_free_access_room = [
			camera_slug
			for camera_slug, camera_data in cameras.items()
			if camera_data[DATA_ROOM] == lock_data[DATA_ROOM_WITH_FREE_ACCESS]
		]
		cameras_in_the_limited_access_room = [
			camera_slug
			for camera_slug, camera_data in cameras.items()
			if camera_data[DATA_ROOM] == lock_data[DATA_ROOM_WITH_LIMITED_ACCESS]
		]

		cameras_in_the_free_access_room_that_show_the_lock = [
			camera_slug
			for camera_slug in cameras_in_the_free_access_room
			if lock_slug in cameras[camera_slug][DATA_IN_VIEW][DATA_LOCKS]
		]
		cameras_in_the_limited_access_room_that_show_the_lock = [
			camera_slug
			for camera_slug in cameras_in_the_limited_access_room
			if lock_slug in cameras[camera_slug][DATA_IN_VIEW][DATA_LOCKS]
		]
		other_cameras_that_show_the_lock = [
			camera_slug
			for camera_slug, camera_data in cameras.items()
			if camera_slug not in cameras_in_the_free_access_room
			and camera_slug not in cameras_in_the_limited_access_room
			and lock_slug in camera_data[DATA_IN_VIEW][DATA_LOCKS]
		]

		cameras_in_the_free_access_room_that_do_not_show_the_lock = [
			camera_slug
			for camera_slug in cameras_in_the_free_access_room
			if camera_slug not in cameras_in_the_free_access_room_that_show_the_lock
		]
		cameras_in_the_limited_access_room_that_do_not_show_the_lock = [
			camera_slug
			for camera_slug in cameras_in_the_limited_access_room
			if camera_slug not in cameras_in_the_limited_access_room_that_show_the_lock
		]

		cameras_showing_the_action = [
			*cameras_in_the_limited_access_room_that_show_the_lock,
			*cameras_in_the_free_access_room_that_show_the_lock,
			*cameras_in_the_limited_access_room_that_do_not_show_the_lock,
			*cameras_in_the_free_access_room_that_do_not_show_the_lock,
			*other_cameras_that_show_the_lock,
		]
		if cameras_showing_the_action:
			notify_args[DATA_CAMERA] = cameras_showing_the_action[0]

		if matching_garage_doors:
			notify_args[DATA_ACTIONS] = [
				{
					DATA_ID: f"{DATA_CLOSE_GARAGE_DOOR}_{garage_door_slug}",
				}
				for garage_door_slug in matching_garage_doors
			]

		async def set_zone_and_room():
			zone_input_select_entity_id = (
				f"{DOMAIN_INPUT_SELECT}.{person_slug}_{DATA_ZONE}"
			)
			current_zone = hass.states.get(zone_input_select_entity_id).state

			await hass.services.async_call(
				DOMAIN_INPUT_SELECT,
				SERVICE_SELECT_OPTION,
				{
					CONF_ENTITY_ID: zone_input_select_entity_id,
					CONF_OPTION: lock_data[DATA_ZONE],
				},
				blocking=True,
			)

			if current_zone == OPTION_UNTRACKABLE:
				await sleep(0)

				await hass.services.async_call(
					DOMAIN_INPUT_SELECT,
					SERVICE_SELECT_OPTION,
					{
						CONF_ENTITY_ID: zone_input_select_entity_id,
						CONF_OPTION: OPTION_UNTRACKABLE,
					},
					blocking=True,
				)

			room_input_select_entity_id = (
				f"{DOMAIN_INPUT_SELECT}.{person_slug}_{DATA_ROOM}"
			)
			await hass.services.async_call(
				DOMAIN_INPUT_SELECT,
				SERVICE_SELECT_OPTION,
				{
					CONF_ENTITY_ID: room_input_select_entity_id,
					CONF_OPTION: lock_data[DATA_ROOM_WITH_LIMITED_ACCESS],
				},
				blocking=True,
			)

			await sleep(1)

			await hass.services.async_call(
				DOMAIN_INPUT_SELECT,
				SERVICE_SELECT_OPTION,
				{
					CONF_ENTITY_ID: room_input_select_entity_id,
					CONF_OPTION: lock_data[DATA_ROOM_WITH_FREE_ACCESS],
				},
				blocking=True,
			)

		set_zone_and_room_task = set_zone_and_room()

		same_device_notify_tasks = []
		for os, os_data in phone_data[DATA_OSES].items():
			mobile_app_data = os_data[DATA_BROWSERS].get(BROWSER_MOBILE_APP)

			if mobile_app_data is None:
				continue

			title = "Unlocking the Door"
			message = (
				f"The {lock_data[DATA_FULL_NAME].lower()} is being unlocked now!"
			)
			image = IMAGE_LOCK_UNLOCKED_COLOR

			same_device_notify_tasks.append(
				notify_mobile_app(
					actions=None,
					camera=None,
					channel=None,
					color=None,
					group=None,
					image=image,
					map=None,
					message=message,
					message_html=message,
					os=os,
					priority=PRIORITY_EMERGENCY,  # TODO: not really an emergency but should be TTS
					push_sound=None,
					replace=None,
					slug=mobile_app_data[DATA_SLUG],
					subtitle=None,
					title=title,
					title_html=title,
					tts=message,
					use_speaker=True,
					hass=hass,
				)
			)

		await gather(*same_device_notify_tasks, unlock_task, notify_task, set_zone_and_room_task)

	return unlock_this_lock


async def do_nothing(*, event, hass, tag_data):
	_LOGGER.error(event)


async def get_tags(**kwds):
	# TODO: this shouldn't work like this...
	cameras = await get_cameras(**kwds)
	garage_doors = await get_garage_doors(**kwds)
	locks = await get_locks(**kwds)
	people = await get_people(**kwds)
	phones = await get_phones(**kwds)
	windows = await get_windows(**kwds)

	tags = {
		"0e52c6f4-12da-4491-97a3-65c9c2e2021e": {
			DATA_ACTION: do_nothing,
			DATA_FULL_NAME: "Card - 1",
		},
		"f94b1166-543f-48c6-a03d-774c9b62a269": {
			DATA_ACTION: do_nothing,
			DATA_FULL_NAME: "Keychain - 1",
		},
		"48c727cb-f62b-4507-82d2-83a0dd2beffa": {
			DATA_ACTION: do_nothing,
			DATA_FULL_NAME: "Sticker - Blue NFC 1",
		},
		"fee05f15-5c2c-40a7-a7c0-1617b2699de4": {
			DATA_ACTION: do_nothing,
			DATA_FULL_NAME: "Sticker - Blue NFC 2",
		},
		"073d45b2-5708-43cc-a7fb-c107f3d0ec2c": {
			DATA_ACTION: do_nothing,
			DATA_FULL_NAME: "Sticker - Blue NFC 3",
		},
		"941c30ef-762c-4b35-a8e6-48bfd7685a0f": {
			DATA_ACTION: do_nothing,
			DATA_FULL_NAME: "Sticker - Blue NFC 4",
		},
		"20202489-bf31-48b6-87c2-60cee77ff5ba": {
			DATA_ACTION: do_nothing,
			DATA_FULL_NAME: "Sticker - Blue NFC 5",
		},
		"23d1ddd6-2a8e-4bde-b0ad-d77e331f9331": {
			DATA_ACTION: do_nothing,
			DATA_FULL_NAME: "Sticker - Blue NFC 6",
		},
		"7a2496bc-a460-469c-9a5d-e55f1259a046": {
			DATA_ACTION: toggle_blinds(
				WINDOW_JACOB_S_BEDROOM,
				people=people,
				phones=phones,
				windows=windows,
				kwds=kwds,
			),
			DATA_FULL_NAME: "Sticker - White 1",
			DATA_ROOM: ROOM_JACOB_S_BEDROOM,
			DATA_ZONE: ZONE_BAKA_S_HOUSE,
		},
		"827f6004-00b6-4e80-ba9c-f820447403e6": {
			DATA_ACTION: unlock_a_lock(
				LOCK_FRONT_DOOR,
				cameras=cameras,
				garage_doors=garage_doors,
				locks=locks,
				people=people,
				phones=phones,
				kwds=kwds,
			),
			DATA_FULL_NAME: "Sticker - White 2",  # Sharpied over in black
		},
		"b559513a-812b-479e-937f-2265db2183b4": {
			DATA_ACTION: unlock_a_lock(
				LOCK_DOOR_TO_THE_GARAGE,
				cameras=cameras,
				garage_doors=garage_doors,
				locks=locks,
				people=people,
				phones=phones,
				kwds=kwds,
			),
			DATA_FULL_NAME: "Sticker - White 3",
		},
		"1ff63144-1828-4d05-991c-663e51ddf33b": {
			DATA_ACTION: do_nothing,
			DATA_FULL_NAME: "Sticker - White 4",
		},
		"8c25b14e-955f-422c-8b70-20de05b23dc9": {
			DATA_ACTION: do_nothing,
			DATA_FULL_NAME: "Sticker - White 5",
		},
		"3286a09b-189a-4507-8c32-d66ed377508c": {
			DATA_ACTION: do_nothing,
			DATA_FULL_NAME: "Sticker - White 6",
		},
	}

	return tags

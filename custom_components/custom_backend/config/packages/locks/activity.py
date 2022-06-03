"Notify about the locks"

from asyncio import sleep
from datetime import datetime, timedelta
from logging import getLogger

from homeassistant import core

from custom_components.custom_backend.const import (
	CHANNEL_ATTACKS, CHANNEL_LOCK_ACTIVITY, CONF_ENTITY_ID, CONF_OPTION, DATA_ACTION, DATA_ACTIONS, DATA_ALARMLEVEL, DATA_ALARMTYPE, DATA_AUDIO, DATA_CAMERA, DATA_CAUSE, DATA_CHANNEL, DATA_CLOSE_GARAGE_DOOR, DATA_COLOR, DATA_DATETIME, DATA_FULL_NAME, DATA_GROUP, DATA_ID, DATA_IMAGE, DATA_IN_VIEW, DATA_LOCKS, DATA_LOCK_SLOTS, DATA_MESSAGE, DATA_NICKNAME, DATA_OPEN_GARAGE_DOOR, DATA_PEOPLE, DATA_PERSON, DATA_PRIORITY, DATA_PUSH, DATA_REQUIRE_DEVICE_UNLOCK, DATA_ROOM, DATA_ROOM_WITH_FREE_ACCESS, DATA_ROOM_WITH_LIMITED_ACCESS, DATA_SHORT_NAME, DATA_TEXT, DATA_TITLE, DATA_ZONE, DOMAIN_COVER, DOMAIN_CUSTOM_BACKEND, DOMAIN_INPUT_SELECT, DOMAIN_SENSOR, EVENT_TYPE_HOMEASSISTANT_START, IMAGE_ACCESS_DENIED_COLOR, IMAGE_FRAUD_COLOR, IMAGE_LOCK_UNLOCKED_COLOR, IMAGE_WRONG_PINCODE_COLOR, NOTIFICATION_COLOR_GREEN, NOTIFICATION_COLOR_ORANGERED, NOTIFICATION_COLOR_YELLOW, PRIORITY_NORMAL, PRIORITY_URGENT, PUSH_SOUND_AUTOUNLOCK_HAPTIC, SERVICE_CLOSE_COVER, SERVICE_OPEN_COVER, SERVICE_SELECT_OPTION, SHARED_MEMORY_REMOTE_UNLOCKING
)
from custom_components.custom_backend.utils import entity_state_to_readable_store, window
from custom_components.custom_backend.config.packages.cameras import get_cameras
from custom_components.custom_backend.config.packages.garage_doors import get_garage_doors
from custom_components.custom_backend.config.packages.notify import notify
from custom_components.custom_backend.config.packages.people.zone_tracking import OPTION_UNTRACKABLE

from . import get_locks


_LOGGER = getLogger(__name__)

async def async_setup(hass: core.HomeAssistant, config: dict, **kwds) -> bool:
	people = kwds[DATA_PEOPLE]
	cameras = await get_cameras(**kwds)
	garage_doors = await get_garage_doors(**kwds)
	locks = await get_locks(**kwds)

	async def lock_alarm_type_and_level_changed(*, lock_slug, alarm_type, alarm_level):
		lock_data = locks[lock_slug]
		this_lock_s_rooms = {lock_data[DATA_ROOM_WITH_FREE_ACCESS], lock_data[DATA_ROOM_WITH_LIMITED_ACCESS]}
		matching_garage_doors = [garage_door_slug for garage_door_slug, garage_door_data in garage_doors.items() if garage_door_data[DATA_ROOM_WITH_FREE_ACCESS] in this_lock_s_rooms or garage_door_data[DATA_ROOM_WITH_LIMITED_ACCESS] in this_lock_s_rooms]
		
		cameras_in_the_free_access_room = [camera_slug for camera_slug, camera_data in cameras.items() if camera_data[DATA_ROOM] == lock_data[DATA_ROOM_WITH_FREE_ACCESS]]
		cameras_in_the_limited_access_room = [camera_slug for camera_slug, camera_data in cameras.items() if camera_data[DATA_ROOM] == lock_data[DATA_ROOM_WITH_LIMITED_ACCESS]]

		cameras_in_the_free_access_room_that_show_the_lock = [camera_slug for camera_slug in cameras_in_the_free_access_room if lock_slug in cameras[camera_slug][DATA_IN_VIEW][DATA_LOCKS]]
		cameras_in_the_limited_access_room_that_show_the_lock = [camera_slug for camera_slug in cameras_in_the_limited_access_room if lock_slug in cameras[camera_slug][DATA_IN_VIEW][DATA_LOCKS]]
		other_cameras_that_show_the_lock = [camera_slug for camera_slug, camera_data in cameras.items() if camera_slug not in cameras_in_the_free_access_room and camera_slug not in cameras_in_the_limited_access_room and lock_slug in camera_data[DATA_IN_VIEW][DATA_LOCKS]]

		cameras_in_the_free_access_room_that_do_not_show_the_lock = [camera_slug for camera_slug in cameras_in_the_free_access_room if camera_slug not in cameras_in_the_free_access_room_that_show_the_lock]
		cameras_in_the_limited_access_room_that_do_not_show_the_lock = [camera_slug for camera_slug in cameras_in_the_limited_access_room if camera_slug not in cameras_in_the_limited_access_room_that_show_the_lock]

		notify_args = {}
		
		if alarm_type == "9":
			if alarm_level == "1":
				# TODO: failure to auto-relock because it was jammed
				...
		elif alarm_type == "19":
			lock_slot = int(alarm_level, 10)

			people_whose_only_lock_slot_is_this = set()
			people_who_couldve_unlocked = []
			for person_slug, person_data in people.items():
				if lock_slot in person_data[DATA_LOCK_SLOTS]:
					people_who_couldve_unlocked.append(person_slug)

					if len(person_data[DATA_LOCK_SLOTS]) == 1:
						people_whose_only_lock_slot_is_this.add(person_slug)

			most_likely_unlockers = [person_slug for person_slug in people_who_couldve_unlocked if person_slug in people_whose_only_lock_slot_is_this]
			less_likely_unlockers = [person_slug for person_slug in people_who_couldve_unlocked if person_slug not in most_likely_unlockers]

			get_nickname = lambda person_slug: people[person_slug][DATA_NICKNAME]
			most_likely_unlockers.sort(key=get_nickname)
			less_likely_unlockers.sort(key=get_nickname)

			unlockers_in_order_of_likeliness = [*most_likely_unlockers, *less_likely_unlockers]
			
			most_likely_unlocker = None
			if unlockers_in_order_of_likeliness:
				most_likely_unlocker = unlockers_in_order_of_likeliness[0]
				unlocker = " or ".join([people[person_slug][DATA_NICKNAME] for person_slug in unlockers_in_order_of_likeliness])
			else:
				if lock_slot == 0:
					unlocker = "The master code, WHICH SHOULD NEVER BE USED,"
				else:
					unlocker = f"An unknown person ({lock_slot})"

			notify_args = {
				DATA_AUDIO: {
					DATA_PUSH: PUSH_SOUND_AUTOUNLOCK_HAPTIC,
				},
				DATA_CHANNEL: CHANNEL_LOCK_ACTIVITY,
				DATA_TEXT: {
					DATA_MESSAGE: f"{unlocker} unlocked the {lock_data[DATA_NICKNAME].lower()}!",
					DATA_TITLE: f"{lock_data[DATA_NICKNAME]} Unlocked",
				},
			}
			if most_likely_unlocker is not None:
				notify_args[DATA_CAUSE] = {
					DATA_PERSON: most_likely_unlocker,
				}
				notify_args[DATA_COLOR] = NOTIFICATION_COLOR_GREEN
				notify_args[DATA_IMAGE] = IMAGE_LOCK_UNLOCKED_COLOR
			else:
				notify_args[DATA_COLOR] = NOTIFICATION_COLOR_YELLOW
				notify_args[DATA_GROUP] = "Household Activity"
				notify_args[DATA_PRIORITY] = PRIORITY_URGENT
				notify_args[DATA_IMAGE] = IMAGE_FRAUD_COLOR

			cameras_showing_the_action = [*cameras_in_the_limited_access_room_that_show_the_lock, *cameras_in_the_free_access_room_that_show_the_lock, *cameras_in_the_limited_access_room_that_do_not_show_the_lock, *cameras_in_the_free_access_room_that_do_not_show_the_lock]
			if cameras_showing_the_action:
				notify_args[DATA_CAMERA] = cameras_showing_the_action[0]

			if matching_garage_doors:
				notify_args[DATA_ACTIONS] = [
					{
						DATA_ID: f"{DATA_CLOSE_GARAGE_DOOR}_{garage_door_slug}",
					} for garage_door_slug in matching_garage_doors
				]
			
			if unlockers_in_order_of_likeliness:
				async def set_zone_and_room():
					for person_slug in unlockers_in_order_of_likeliness:
						zone_input_select_entity_id = f"{DOMAIN_INPUT_SELECT}.{person_slug}_{DATA_ZONE}"
						current_zone = hass.states.get(zone_input_select_entity_id).state

						await hass.services.async_call(DOMAIN_INPUT_SELECT, SERVICE_SELECT_OPTION, {
							CONF_ENTITY_ID: zone_input_select_entity_id,
							CONF_OPTION: lock_data[DATA_ZONE],
						}, blocking=True)

						if current_zone == OPTION_UNTRACKABLE:
							await sleep(0)

							await hass.services.async_call(DOMAIN_INPUT_SELECT, SERVICE_SELECT_OPTION, {
								CONF_ENTITY_ID: zone_input_select_entity_id,
								CONF_OPTION: OPTION_UNTRACKABLE,
							}, blocking=True)
						
						room_input_select_entity_id = f"{DOMAIN_INPUT_SELECT}.{person_slug}_{DATA_ROOM}"
						await hass.services.async_call(DOMAIN_INPUT_SELECT, SERVICE_SELECT_OPTION, {
							CONF_ENTITY_ID: room_input_select_entity_id,
							CONF_OPTION: lock_data[DATA_ROOM_WITH_LIMITED_ACCESS],
						}, blocking=True)

						await sleep(1)
						
						await hass.services.async_call(DOMAIN_INPUT_SELECT, SERVICE_SELECT_OPTION, {
							CONF_ENTITY_ID: room_input_select_entity_id,
							CONF_OPTION: lock_data[DATA_ROOM_WITH_FREE_ACCESS],
						}, blocking=True)

				hass.async_create_task(set_zone_and_room())
		elif alarm_type == "21":
			if alarm_level == "1":
				# Manually locked by someone on the inside
				return
			elif alarm_level == "2":
				# Manually locked by someone on the outside (by pressing a button on the keypad)
				return
		elif alarm_type == "22":
			if alarm_level == "1":
				notify_args = {
					DATA_AUDIO: {
						DATA_PUSH: PUSH_SOUND_AUTOUNLOCK_HAPTIC,
					},
					DATA_CHANNEL: CHANNEL_LOCK_ACTIVITY,
					DATA_COLOR: NOTIFICATION_COLOR_GREEN,
					DATA_GROUP: "Household Activity",
					DATA_IMAGE: IMAGE_LOCK_UNLOCKED_COLOR,
					DATA_TEXT: {
						DATA_MESSAGE: f"The {lock_data[DATA_NICKNAME].lower()} was unlocked from the inside!",
						DATA_TITLE: f"{lock_data[DATA_NICKNAME]} Unlocked",
					},
				}
				
				# TODO: make it known that hallway <--> front room is 100% transparent so this is considered a contiguous room group
				cameras_showing_the_action = [*cameras_in_the_free_access_room_that_show_the_lock, *other_cameras_that_show_the_lock, *cameras_in_the_limited_access_room_that_show_the_lock, *cameras_in_the_limited_access_room_that_do_not_show_the_lock, *cameras_in_the_free_access_room_that_do_not_show_the_lock]
				if cameras_showing_the_action:
					notify_args[DATA_CAMERA] = cameras_showing_the_action[0]

				if matching_garage_doors:
					notify_args[DATA_ACTIONS] = [
						{
							DATA_ID: f"{DATA_OPEN_GARAGE_DOOR}_{garage_door_slug}"
						} for garage_door_slug in matching_garage_doors
					]
		elif alarm_type == "24":
			if alarm_level == "1":
				# Locked remotely with Home Assistant
				return
		elif alarm_type == "25":
			if alarm_level == "1":
				do_notify = True
				REMOTE_UNLOCKING = hass.data[DOMAIN_CUSTOM_BACKEND][SHARED_MEMORY_REMOTE_UNLOCKING]
				_LOGGER.warning(f"TODO DEBUGGING: lock alarm changed: REMOTE_UNLOCKING: {REMOTE_UNLOCKING}")
				_LOGGER.warning(f"TODO DEBUGGING: lock alarm changed: lock_slug: {lock_slug}")
				if lock_slug in REMOTE_UNLOCKING:
					remote_unlocking = REMOTE_UNLOCKING.pop(lock_slug)

					time_since_remote_unlock = datetime.now() - remote_unlocking[DATA_DATETIME]

					_LOGGER.warning(f"time_since_remote_unlock: {time_since_remote_unlock}")

					if time_since_remote_unlock < timedelta(seconds=10):
						do_notify = False
				
				if not do_notify:
					return
				
				notify_args = {
					DATA_AUDIO: {
						DATA_PUSH: PUSH_SOUND_AUTOUNLOCK_HAPTIC,
					},
					DATA_CHANNEL: CHANNEL_LOCK_ACTIVITY,
					DATA_COLOR: NOTIFICATION_COLOR_YELLOW,
					DATA_GROUP: "Household Activity",
					DATA_IMAGE: IMAGE_LOCK_UNLOCKED_COLOR,
					DATA_PRIORITY: PRIORITY_URGENT,
					DATA_TEXT: {
						DATA_MESSAGE: f"The {lock_data[DATA_NICKNAME].lower()} was unlocked with Home Assistant by an unknown person!",
						DATA_TITLE: f"{lock_data[DATA_NICKNAME]} Unlocked",
					},
				}
		elif alarm_type == "27":
			if alarm_level == "1":
				# Successful auto re-lock
				return
		elif alarm_type == "112":
			# TODO: master code change
			if alarm_level == "0":
				# TODO: using the keypad
				...
			elif alarm_level == "251":
				# TODO: remotely
				...
		elif alarm_type == "122":
			# TODO: code updated according to online
			...
		elif alarm_type == "161":
			notify_args = {
				DATA_CHANNEL: CHANNEL_ATTACKS,
				DATA_COLOR: NOTIFICATION_COLOR_ORANGERED,
				DATA_PRIORITY: PRIORITY_URGENT,
				DATA_TEXT: {
					DATA_TITLE: f"{lock_data[DATA_FULL_NAME]} Alarm",
				},
			}
			if alarm_level == "1":
				notify_args.update({
					DATA_IMAGE: IMAGE_ACCESS_DENIED_COLOR,
				})
				notify_args[DATA_TEXT].update({
					DATA_MESSAGE: f"Someone is at the {lock_data[DATA_NICKNAME].lower()}!",
				})
			elif alarm_level == "2":
				notify_args.update({
					DATA_IMAGE: IMAGE_FRAUD_COLOR,
				})
				notify_args[DATA_TEXT].update({
					DATA_MESSAGE: f"Someone is trying to break in the {lock_data[DATA_NICKNAME].lower()}! They are breaking the lock!",
				})
			elif alarm_level == "3":
				notify_args.update({
					DATA_IMAGE: IMAGE_WRONG_PINCODE_COLOR,
				})
				notify_args[DATA_TEXT].update({
					DATA_MESSAGE: f"Someone is trying to hack the {lock_data[DATA_FULL_NAME].lower()} by guessing the pass code!",
				})
		elif alarm_type == "167":
			# TODO: this is wrong (fix)
			notify_args = {
				DATA_AUDIO: {
					# TODO: what was the battery sound??
					# DATA_PUSH: PUSH_SOUND_AUTOUNLOCK_HAPTIC,
				},
				DATA_CHANNEL: CHANNEL_LOCK_ACTIVITY,
				# TODO: check
				DATA_COLOR: NOTIFICATION_COLOR_ORANGERED,
				DATA_IMAGE: IMAGE_LOCK_UNLOCKED_COLOR,
				DATA_PRIORITY: PRIORITY_URGENT,
				DATA_TEXT: {
					DATA_MESSAGE: f"The {lock_data[DATA_NICKNAME].lower()} batteries are low!",
					DATA_TITLE: f"{lock_data[DATA_NICKNAME]} Batteries",
				},
			}
			# TODO: battery alert
			...
		elif alarm_type == "168":
			# TODO: battery alert
			...

		if notify_args:
			await notify(notify_args, hass=hass, **kwds)
		else:
			# TODO: debug
			_LOGGER.error(f"UNACKNOWLEDGED: called lock_alarm_type_and_level_changed: {lock_slug} {alarm_type} {alarm_level}")


	async def get_and_check_alarm_types_and_levels(*, lock_slug):
		lock_data = locks[lock_slug]

		alarm_level = hass.states.get(f"{DOMAIN_SENSOR}.{lock_data[DATA_ALARMLEVEL]}").state
		alarm_type = hass.states.get(f"{DOMAIN_SENSOR}.{lock_data[DATA_ALARMTYPE]}").state

		await lock_alarm_type_and_level_changed(lock_slug=lock_slug, alarm_type=alarm_type, alarm_level=alarm_level)

	async def setup_automations(event):
		for lock_slug, lock_data in locks.items():
			# TODO: add back f"{DOMAIN_SENSOR}.{lock_data[DATA_ALARMLEVEL]}", if needed
			[_get_lock_alarm_level_changes, subscribe_to_lock_alarm_level_changes] = window(entity_state_to_readable_store(f"{DOMAIN_SENSOR}.{lock_data[DATA_ALARMLEVEL]}", hass=hass), 2)
			subscribe_to_lock_alarm_level_changes(lambda *, lock_slug=lock_slug: hass.async_create_task(get_and_check_alarm_types_and_levels(lock_slug=lock_slug)))

	hass.bus.async_listen(EVENT_TYPE_HOMEASSISTANT_START, setup_automations)
	return True

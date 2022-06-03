"Set up the notification service"

from asyncio import gather
from datetime import datetime, timedelta
from logging import getLogger
from custom_components.custom_backend.config.packages.notify.image_manipulation import badge_image

from homeassistant import core

from custom_components.custom_backend.const import BROWSER_MOBILE_APP, CONF_DEVICEID, CONF_DURATION, CONF_ENTITY_ID, CONF_MESSAGE, CONF_PLATFORM, CONF_SERVICE_NAME, CONF_TIME_MEMORY, DATA_ACTION, DATA_ACTIONS, DATA_AUDIO, DATA_BROWSERS, DATA_BROWSER_MOD, DATA_CAMERA, DATA_CAUSE, DATA_CHANNEL, DATA_CHROMECAST, DATA_CLOSE_GARAGE_DOOR, DATA_COLOR, DATA_COMPUTERS, DATA_DATETIME, DATA_DEVICES, DATA_FULL_NAME, DATA_GROUP, DATA_HOME, DATA_ICON, DATA_ID, DATA_IMAGE, DATA_LATITUDE, DATA_LONGITUDE, DATA_MAP, DATA_MESSAGE, DATA_MESSAGE_HTML, DATA_MOBILE_APP, DATA_NICKNAME, DATA_OPEN_GARAGE_DOOR, DATA_OSES, DATA_PEOPLE, DATA_PERSON, DATA_PHONES, DATA_PHOTO, DATA_PRIORITY, DATA_PUSH, DATA_REPLACE, DATA_REQUIRE_DEVICE_UNLOCK, DATA_ROOM, DATA_ROOMS, DATA_SATURATION, DATA_SECRETS, DATA_SHORT_NAME, DATA_SLUG, DATA_SSML, DATA_TABLETS, DATA_TEXT, DATA_TITLE, DATA_TITLE_HTML, DATA_TTS, DATA_UNLOCK_LOCK, DATA_ZONE, DEVICE_TYPES, DEVICE_TYPE_COMPUTER, DEVICE_TYPE_LIGHT, DEVICE_TYPE_PHONE, DEVICE_TYPE_SPEAKER, DEVICE_TYPE_TABLET, DOMAIN_BROWSER_MOD, DOMAIN_CAMERA, DOMAIN_COVER, DOMAIN_CUSTOM_BACKEND, DOMAIN_INPUT_SELECT, DOMAIN_LOCK, DOMAIN_MEDIA_PLAYER, DOMAIN_TTS, EVENT_TYPE_MOBILE_APP_NOTIFICATION_ACTION, PLATFORM_GOOGLE_TRANSLATE, PRIORITY_EMERGENCY, PRIORITY_NORMAL, PRIORITY_URGENT, PUSH_SOUND_3RD_PARTY_CRITICAL, PUSH_SOUND_SWTEST1_HAPTIC, SERVICE_CLOSE_COVER, SERVICE_GOOGLE_SAY, SERVICE_NOTIFY, SERVICE_OPEN_COVER, SERVICE_TOAST, SERVICE_UNLOCK, SHARED_MEMORY_EVERPRESENT_NOTIFICATION_ACTIONS, SHARED_MEMORY_NOTIFICATION_ACTIONS, SHARED_MEMORY_NOTIFICATION_LIGHTS, ZONE_BAKA_S_HOUSE

from custom_components.custom_backend.config.packages.computers import get_computers
from custom_components.custom_backend.config.packages.phones import get_phones
from custom_components.custom_backend.config.packages.speakers import get_speakers
from custom_components.custom_backend.config.packages.tablets import get_tablets

from .image_manipulation import badge_image
from .mobile_app import notify_mobile_app

_LOGGER = getLogger(__name__)


async def notify_browser_mod(*, device_id, duration, message, title, hass):
	message = f"{title}: {message}"
	
	if duration is None:
		duration = 60*len(message) + 3600

	await hass.services.async_call(
		DOMAIN_BROWSER_MOD,
		SERVICE_TOAST,
		{
			CONF_DEVICEID: device_id,
			CONF_DURATION: duration,
			CONF_MESSAGE: message,
		},
		blocking=True
	)


async def notify_chromecast(*, slug, tts, hass):
	# TODO: full implementation of chromecast_tts
	await hass.services.async_call(DOMAIN_TTS, SERVICE_GOOGLE_SAY, {
		CONF_ENTITY_ID: f"{DOMAIN_MEDIA_PLAYER}.{slug}",
		CONF_MESSAGE: tts,
	}, blocking=True)


async def notify(data, *, hass, **kwds):
	secrets = kwds[DATA_SECRETS]
	all_people = kwds[DATA_PEOPLE]

	now = datetime.now()

	# Cause of this notification
	cause = data.get(DATA_CAUSE, {})
	caused_by_person = cause.get(DATA_PERSON)

	# Color (for lights and Android accents and eventually emails)
	color = data.get(DATA_COLOR, None)

	# Priority
	priority = data.get(DATA_PRIORITY, PRIORITY_NORMAL)

	# Replace previous notification or let it stay
	replace = data.get(DATA_REPLACE)

	# Text configuration
	text = data.get(DATA_TEXT, {})
	title = text.get(DATA_TITLE, None)
	title_html = text.get(DATA_TITLE_HTML, title)
	subtitle = None
	message = text.get(DATA_MESSAGE, None)
	message_html = text.get(DATA_MESSAGE_HTML, message)

	# Audio configuration
	audio = data.get(DATA_AUDIO, {})
	tts = audio.get(DATA_TTS, message)
	ssml = audio.get(DATA_SSML, f"<speak>{tts}</speak>")
	push_sound = audio.get(DATA_PUSH, {
		PRIORITY_URGENT: PUSH_SOUND_3RD_PARTY_CRITICAL,
		PRIORITY_EMERGENCY: PUSH_SOUND_SWTEST1_HAPTIC,
	}.get(priority))

	# Icons and images
	BASE_WEBSITE = secrets["website_home_assistant"]
	image = data.get(DATA_IMAGE)
	if image is None:
		if caused_by_person is not None:
			image = all_people[caused_by_person][DATA_PHOTO]
	else:
		if caused_by_person is not None:
			image = await badge_image(all_people[caused_by_person][DATA_PHOTO], image)
	
	if image is not None:
		if image.startswith("/"):
			image = f"{BASE_WEBSITE}{image}"
		
		if not image.startswith("https://"):
			image = f"{BASE_WEBSITE}{image}"


	# Notification group
	group = data.get(DATA_GROUP)
	if group is None:
		if caused_by_person is not None:
			group = f"{all_people[caused_by_person][DATA_FULL_NAME]}'s Activity"

	# Notification channel
	channel = data.get(DATA_CHANNEL)

	# Should a map be attached to the notification?
	map = data.get(DATA_MAP)

	# Should a camera stream be attached to the notification?
	camera = data.get(DATA_CAMERA)

	# Should any action buttons be attached to the notification?
	actions = data.get(DATA_ACTIONS)

	# Where should this notification be received?
	rooms_to_notify = data.get(DATA_ROOMS)
	if rooms_to_notify is None:
		rooms_to_notify = []
	rooms_to_notify = set(rooms_to_notify)
	
	# What types of devices should this notification be received on?
	device_types_to_notify = data.get(DATA_DEVICES)
	if device_types_to_notify is None:
		device_types_to_notify = DEVICE_TYPES
	device_types_to_notify = set(device_types_to_notify)
	
	# Who should receive this notification?
	people_to_notify = data.get(DATA_PEOPLE)
	people_to_notify = data.get(DATA_PEOPLE)
	if people_to_notify is None:
		people_who_live_at_baka_s_house = [person_slug for person_slug, person_data in all_people.items() if person_data[DATA_HOME] == ZONE_BAKA_S_HOUSE]
		# TODO: priority check I guess???
		# Do not notify someone of their own activity
		people_to_notify = [person_slug for person_slug in people_who_live_at_baka_s_house if person_slug != caused_by_person]
	# if rooms_to_notify is None:

	[all_computers, all_phones, all_speakers, all_tablets] = await gather(get_computers(**kwds), get_phones(**kwds), get_speakers(**kwds), get_tablets(**kwds))

	notification_tasks = []

	def add_notification_tasks(*, all_devices, device_type, person_data_key):
		if device_type not in device_types_to_notify:
			return
		
		for device_slug in person_data[person_data_key]:
			for os_name, os_data in all_devices[device_slug][DATA_OSES].items():
				for browser_name, browser_data in os_data[DATA_BROWSERS].items():
					if browser_name == BROWSER_MOBILE_APP:
						notification_tasks.append(notify_mobile_app(actions=actions, camera=camera, channel=channel, color=color, group=group, image=image, map=map, message=message, message_html=message_html, os=os_name, priority=priority, push_sound=push_sound, replace=replace, slug=browser_data[DATA_SLUG], subtitle=subtitle, title=title, title_html=title_html, tts=tts, use_speaker=DEVICE_TYPE_SPEAKER in device_types_to_notify, hass=hass))
					
					notification_tasks.append(notify_browser_mod(device_id=browser_data[DATA_BROWSER_MOD], duration=None, message=message, title=title, hass=hass))
	
	
	for person_slug in people_to_notify:
		person_data = all_people[person_slug]

		add_notification_tasks(all_devices=all_computers, device_type=DEVICE_TYPE_COMPUTER, person_data_key=DATA_COMPUTERS)
		add_notification_tasks(all_devices=all_phones, device_type=DEVICE_TYPE_PHONE, person_data_key=DATA_PHONES)
		add_notification_tasks(all_devices=all_tablets, device_type=DEVICE_TYPE_TABLET, person_data_key=DATA_TABLETS)

		person_zone = hass.states.get(f"{DOMAIN_INPUT_SELECT}.{person_slug}_{DATA_ZONE}").state

		if person_zone == ZONE_BAKA_S_HOUSE:
			person_room = hass.states.get(f"{DOMAIN_INPUT_SELECT}.{person_slug}_{DATA_ROOM}").state

			rooms_to_notify.add(person_room)
	
	if DEVICE_TYPE_LIGHT in device_types_to_notify:
		notification_light_stores = hass.data[SHARED_MEMORY_NOTIFICATION_LIGHTS]

		if color is None:
			_LOGGER.warning(f"can't set a notification light color for {title}: {message}")
		else:
			for room_name in rooms_to_notify:
				notification_light_store = notification_light_stores[room_name]
				[set_value, *_readable_notification_light_store] = notification_light_store
				set_value({
					DATA_COLOR: color[DATA_COLOR],
					DATA_DATETIME: now,
					DATA_SATURATION: color[DATA_SATURATION],
				})


	if DEVICE_TYPE_SPEAKER in device_types_to_notify:
		for speaker_slug, speaker_data in all_speakers.items():
			if speaker_data[DATA_ROOM] not in rooms_to_notify:
				continue
			
			# TODO: reenable
			# notification_tasks.append(notify_chromecast(slug=speaker_data[DATA_CHROMECAST], tts=tts, hass=hass))
			# TODO: switch to camera stream after TTS


	await gather(*notification_tasks)


async def generate_yaml(**kwds):
	return {
		DOMAIN_TTS: [
			{
				CONF_PLATFORM: PLATFORM_GOOGLE_TRANSLATE,
				CONF_SERVICE_NAME: SERVICE_GOOGLE_SAY,
				CONF_TIME_MEMORY: timedelta(hours=2).total_seconds(),
			}
		]
	}


async def async_setup(hass: core.HomeAssistant, config: dict, **kwds):
	hass.data.setdefault(DOMAIN_CUSTOM_BACKEND, {})
	everpresent_actions_map = hass.data[DOMAIN_CUSTOM_BACKEND].setdefault(SHARED_MEMORY_EVERPRESENT_NOTIFICATION_ACTIONS, {})
	actions_map = hass.data[DOMAIN_CUSTOM_BACKEND].setdefault(SHARED_MEMORY_NOTIFICATION_ACTIONS, {})

	async def handle_notify(call):
		await notify(call.data, hass=hass, **kwds)

	hass.services.async_register(DOMAIN_CUSTOM_BACKEND, SERVICE_NOTIFY, handle_notify)

	async def setup_everpresent_actions():
		from custom_components.custom_backend.config.packages.locks import get_locks
		from custom_components.custom_backend.config.packages.garage_doors import get_garage_doors

		garage_doors = await get_garage_doors(**kwds)
		locks = await get_locks(**kwds)

		def do_thing_to_garage_door(garage_door_slug, operation):
			async def do_thing_to_garage_door(*, event, hass):
				await hass.services.async_call(
					DOMAIN_COVER,
					operation,
					{
						CONF_ENTITY_ID: f"{DOMAIN_COVER}.{garage_door_slug}",
					},
					blocking=True
				)
				_LOGGER.warning(f"hi, I'm gonna do {operation} to the {garage_door_slug}. here's the event for it: {event}")
			
			return do_thing_to_garage_door

		for garage_door_slug, garage_door_data in garage_doors.items():
			everpresent_actions_map[f"{DATA_OPEN_GARAGE_DOOR}_{garage_door_slug}"] = {
				DATA_ACTION: do_thing_to_garage_door(garage_door_slug, SERVICE_OPEN_COVER),
				DATA_FULL_NAME: f"Open the {garage_door_data[DATA_FULL_NAME]}",
				DATA_REQUIRE_DEVICE_UNLOCK: True,
				DATA_SHORT_NAME: f"⬆️ {garage_door_data[DATA_NICKNAME]}",
			}

			everpresent_actions_map[f"{DATA_CLOSE_GARAGE_DOOR}_{garage_door_slug}"] = {
				DATA_ACTION: do_thing_to_garage_door(garage_door_slug, SERVICE_CLOSE_COVER),
				DATA_FULL_NAME: f"Close the {garage_door_data[DATA_FULL_NAME]}",
				DATA_REQUIRE_DEVICE_UNLOCK: False,
				DATA_SHORT_NAME: f"⬇️ {garage_door_data[DATA_NICKNAME]}",
			}

		def unlock_lock(lock_slug):
			async def unlock_the_lock(*, event, hass):
				await hass.services.async_call(
					DOMAIN_LOCK,
					SERVICE_UNLOCK,
					{
						CONF_ENTITY_ID: f"{DOMAIN_LOCK}.{lock_slug}",
					},
					blocking=True
				)
				_LOGGER.warning(f"hi, I'm gonna unlock the {lock_slug}. here's the event for it: {event}")
			
			return unlock_the_lock

		for lock_slug, lock_data in locks.items():
			everpresent_actions_map[f"{DATA_UNLOCK_LOCK}_{lock_slug}"] = {
				DATA_ACTION: unlock_lock(lock_slug),
				DATA_FULL_NAME: f"Unlock the {lock_data[DATA_FULL_NAME]}",
				DATA_REQUIRE_DEVICE_UNLOCK: True,
				DATA_SHORT_NAME: f"🔓 {lock_data[DATA_NICKNAME]}",
			}

		actions_map.update(everpresent_actions_map)

	
	# TODO: staging
	async def mobile_app_notification_action_requested(event):
		_LOGGER.error(actions_map)
		requested_action_id = event.data["action"]

		if requested_action_id in everpresent_actions_map:
			action_data = actions_map[requested_action_id]
			await action_data[DATA_ACTION](event=event, hass=hass)
		elif requested_action_id in actions_map:
			action_data = actions_map.pop(requested_action_id)
			await action_data[DATA_ACTION](event=event, hass=hass)
		else:
			# TODO: figure out how to find this device to alert them
			_LOGGER.error(event)
			_LOGGER.error(event.data)
			_LOGGER.warning(dir(event))


	await setup_everpresent_actions()
	hass.bus.async_listen(EVENT_TYPE_MOBILE_APP_NOTIFICATION_ACTION, mobile_app_notification_action_requested)

	return True

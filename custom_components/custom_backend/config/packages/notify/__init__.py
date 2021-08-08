"Set up the notification service"

from asyncio import gather
from logging import getLogger
from uuid import uuid4

from homeassistant import core

from custom_components.custom_backend.const import BROWSER_MOBILE_APP, CONF_ACTION, CONF_ACTIONS, CONF_ACTION_DATA, CONF_AUTHENTICATIONREQUIRED, CONF_CHANNEL, CONF_CLICKACTION, CONF_CRITICAL, CONF_DATA, CONF_DEVICEID, CONF_DURATION, CONF_ENTITY_ID, CONF_GROUP, CONF_ICON_URL, CONF_IMAGE, CONF_IMPORTANCE, CONF_LATITUDE, CONF_LONGITUDE, CONF_MESSAGE, CONF_NAME, CONF_PRIORITY, CONF_PUSH, CONF_SHOWS_COMPASS, CONF_SHOWS_POINTS_OF_INTEREST, CONF_SHOWS_SCALE, CONF_SHOWS_TRAFFIC, CONF_SHOWS_USER_LOCATION, CONF_SOUND, CONF_SUBTITLE, CONF_TAG, CONF_TITLE, CONF_TTL, CONF_URL, CONF_VOLUME, DATA_ACTION, DATA_ACTIONS, DATA_AUDIO, DATA_BROWSERS, DATA_BROWSER_MOD, DATA_CAMERA, DATA_CAUSE, DATA_CHANNEL, DATA_CLOSE_GARAGE_DOOR, DATA_COMPUTERS, DATA_DEVICES, DATA_FULL_NAME, DATA_GROUP, DATA_HOME, DATA_ICON, DATA_ID, DATA_IMAGE, DATA_LATITUDE, DATA_LONGITUDE, DATA_MAP, DATA_MESSAGE, DATA_MESSAGE_HTML, DATA_MOBILE_APP, DATA_NICKNAME, DATA_OPEN_GARAGE_DOOR, DATA_OSES, DATA_PEOPLE, DATA_PERSON, DATA_PHONES, DATA_PHOTO, DATA_PRIORITY, DATA_PUSH, DATA_REPLACE, DATA_REQUIRE_DEVICE_UNLOCK, DATA_ROOMS, DATA_SHORT_NAME, DATA_SLUG, DATA_SSML, DATA_TABLETS, DATA_TEXT, DATA_TITLE, DATA_TITLE_HTML, DATA_TTS, DEVICE_TYPES, DEVICE_TYPE_COMPUTER, DEVICE_TYPE_PHONE, DEVICE_TYPE_SPEAKER, DEVICE_TYPE_TABLET, DOMAIN_BROWSER_MOD, DOMAIN_CAMERA, DOMAIN_COVER, DOMAIN_CUSTOM_BACKEND, DOMAIN_NOTIFY, EVENT_TYPE_MOBILE_APP_NOTIFICATION_ACTION, OS_ANDROID, OS_IOS, OS_MACOS, PRIORITY_EMERGENCY, PRIORITY_LOW, PRIORITY_NORMAL, PRIORITY_URGENT, PUSH_SOUND_3RD_PARTY_CRITICAL, PUSH_SOUND_DEFAULT, PUSH_SOUND_SWTEST1_HAPTIC, SERVICE_CLOSE_COVER, SERVICE_NOTIFY, SERVICE_OPEN_COVER, SERVICE_TOAST, SHARED_EVERPRESENT_NOTIFICATION_ACTIONS, SHARED_NOTIFICATION_ACTIONS, ZONE_BAKA_S_HOUSE

from custom_components.custom_backend.config.packages.computers import get_computers
from custom_components.custom_backend.config.packages.phones import get_phones
from custom_components.custom_backend.config.packages.tablets import get_tablets


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

async def notify_mobile_app(*, actions, camera, channel, group, image, map, message, message_html, os, priority, push_sound, replace, slug, subtitle, title, title_html, tts, use_speaker, hass):
	if replace is None:
		replace = False

	if subtitle is None:
		if actions is not None:
			if os == OS_IOS:
				subtitle = "Action buttons available by long pressing the notification or pulling down the handle"
				if camera is not None:
					subtitle = "Live stream and action buttons available by long pressing the notification or pulling down the handle"
				elif map is not None:
					subtitle = "Map and action buttons available by long pressing the notification or pulling down the handle"
		else:
			if os == OS_IOS:
				if camera is not None:
					subtitle = "Live stream available by long pressing the notification or pulling down the handle"
				elif map is not None:
					subtitle = "Map available by long pressing the notification or pulling down the handle"
	
	service_args = {
		CONF_DATA: {}
	}

	if actions is not None:
		_LOGGER.warning(f"actions: {actions}")

		ACTIONS_MAP = hass.data[DOMAIN_CUSTOM_BACKEND][SHARED_NOTIFICATION_ACTIONS]

		action_ids = []
		for action_data in actions:
			action_id = action_data.get(DATA_ID)
			if action_id is None:
				action_id = f"{DATA_ACTION}_{uuid4()}"
				ACTIONS_MAP[action_id] = action_data
			action_ids.append(action_id)


		if os == OS_ANDROID:
			service_args[CONF_DATA][CONF_ACTIONS] = [
				{
					CONF_ACTION: action_id,
					CONF_TITLE: ACTIONS_MAP[action_id][DATA_SHORT_NAME],
				} for action_id in action_ids
			]
		elif os == OS_IOS:
			service_args[CONF_DATA][CONF_ACTIONS] = [
				{
					CONF_ACTION: action_id,
					CONF_AUTHENTICATIONREQUIRED: ACTIONS_MAP[action_id].get(DATA_REQUIRE_DEVICE_UNLOCK, False),
					CONF_TITLE: ACTIONS_MAP[action_id][DATA_FULL_NAME],
				} for action_id in action_ids
			]

	if camera is not None:
		if os == OS_ANDROID:
			service_args[CONF_DATA][CONF_CLICKACTION] = f"entityId:{DOMAIN_CAMERA}.{camera}"
			service_args[CONF_DATA][CONF_IMAGE] = f"/api/camera_proxy/{DOMAIN_CAMERA}.{camera}"
		elif os in {OS_IOS, OS_MACOS}:
			service_args[CONF_DATA][CONF_URL] = "/devices-by-type/cameras"
			service_args[CONF_DATA][CONF_ENTITY_ID] = f"{DOMAIN_CAMERA}.{camera}"
	
	if channel is not None:
		if os == OS_ANDROID:
			service_args[CONF_DATA][CONF_CHANNEL] = channel

			if priority == PRIORITY_LOW:
				service_args[CONF_DATA][CONF_IMPORTANCE] = "low"
			elif priority == PRIORITY_NORMAL:
				service_args[CONF_DATA][CONF_IMPORTANCE] = "default"
			elif priority == PRIORITY_URGENT:
				service_args[CONF_DATA][CONF_IMPORTANCE] = "high"
			elif priority == PRIORITY_EMERGENCY:
				service_args[CONF_DATA][CONF_IMPORTANCE] = "high"

	if group is not None:
		service_args[CONF_DATA][CONF_GROUP] = group

	if image is not None:
		if os == OS_ANDROID:
			service_args[CONF_DATA][CONF_ICON_URL] = image
		elif os == OS_IOS:
			service_args[CONF_DATA][CONF_IMAGE] = image
		elif os == OS_MACOS:
			if camera is None:
				service_args[CONF_DATA][CONF_IMAGE] = image

	if map is not None:
		service_args[CONF_DATA][CONF_ACTION_DATA] = {
			CONF_LATITUDE: str(map[DATA_LATITUDE]),
			CONF_LONGITUDE: str(map[DATA_LONGITUDE]),
			CONF_SHOWS_COMPASS: True,
			CONF_SHOWS_POINTS_OF_INTEREST: True,
			CONF_SHOWS_SCALE: True,
			CONF_SHOWS_TRAFFIC: True,
			CONF_SHOWS_USER_LOCATION: True,
		}

	if replace:
		service_args[CONF_DATA][CONF_TAG] = group

	if priority == PRIORITY_EMERGENCY:
		if os == OS_ANDROID:
			service_args[CONF_DATA][CONF_PRIORITY] = "high"
			service_args[CONF_DATA][CONF_TTL] = 0
		elif os in {OS_IOS, OS_MACOS}:
			push_config = service_args[CONF_DATA].setdefault(CONF_PUSH, {})
			sound_config = push_config.setdefault(CONF_SOUND, {})
			sound_config[CONF_CRITICAL] = 1
			sound_config[CONF_VOLUME] = 1.0

	if push_sound is not None:
		if os in {OS_IOS, OS_MACOS}:
			push_config = service_args[CONF_DATA].setdefault(CONF_PUSH, {})
			sound_config = push_config.setdefault(CONF_SOUND, {})
			sound_config[CONF_NAME] = push_sound

	if subtitle is not None:
		if os == OS_ANDROID:
			service_args[CONF_MESSAGE] = f"{message_html}\n{subtitle}"
		elif os in {OS_IOS, OS_MACOS}:
			service_args[CONF_DATA][CONF_SUBTITLE] = message
			service_args[CONF_MESSAGE] = subtitle
	else:
		if os == OS_ANDROID:
			service_args[CONF_MESSAGE] = message_html
		elif os in {OS_IOS, OS_MACOS}:
			service_args[CONF_MESSAGE] = message
	
	if title is not None:
		if os == OS_ANDROID:
			service_args[CONF_TITLE] = title_html
		elif os in {OS_IOS, OS_MACOS}:
			service_args[CONF_TITLE] = title

	
	_LOGGER.warning(service_args)

	await hass.services.async_call(
		DOMAIN_NOTIFY,
		f"{DATA_MOBILE_APP}_{slug}",
		service_args,
		blocking=True,
	)

	if use_speaker:
		if os == OS_ANDROID:
			if priority in {PRIORITY_URGENT, PRIORITY_EMERGENCY}:
				tts_service_args = {
					CONF_DATA: {},
					CONF_MESSAGE: "TTS",
					CONF_TITLE: tts,
				}

				if priority == PRIORITY_EMERGENCY:
					tts_service_args[CONF_DATA][CONF_CHANNEL] = "alarm_stream_max"

				await hass.services.async_call(
					DOMAIN_NOTIFY,
					f"{DATA_MOBILE_APP}_{slug}",
					tts_service_args,
					blocking=True,
				)


async def notify(data, *, hass, **kwds):
	secrets = kwds["secrets"]
	all_people = kwds["people"]

	# Cause of this notification
	cause = data.get(DATA_CAUSE, {})
	caused_by_person = cause.get(DATA_PERSON)

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
		# image = "home-assistant.png"
		if caused_by_person is not None:
			image = all_people[caused_by_person][DATA_PHOTO]
	
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

	[all_computers, all_phones, all_tablets] = await gather(get_computers(**kwds), get_phones(**kwds), get_tablets(**kwds))

	def add_notification_tasks(*, all_devices, device_type, person_data_key):
		if device_type in device_types_to_notify:
			for device_slug in person_data[person_data_key]:
				for os_name, os_data in all_devices[device_slug][DATA_OSES].items():
					for browser_name, browser_data in os_data[DATA_BROWSERS].items():
						if browser_name == BROWSER_MOBILE_APP:
							notification_tasks.append(notify_mobile_app(actions=actions, camera=camera, channel=channel, group=group, image=image, map=map, message=message, message_html=message_html, os=os_name, priority=priority, push_sound=push_sound, replace=replace, slug=browser_data[DATA_SLUG], subtitle=subtitle, title=title, title_html=title_html, tts=tts, use_speaker=DEVICE_TYPE_SPEAKER in device_types_to_notify, hass=hass))
						
						notification_tasks.append(notify_browser_mod(device_id=browser_data[DATA_BROWSER_MOD], duration=None, message=message, title=title, hass=hass))
	

	notification_tasks = []
	for person_slug in people_to_notify:
		person_data = all_people[person_slug]

		add_notification_tasks(all_devices=all_computers, device_type=DEVICE_TYPE_COMPUTER, person_data_key=DATA_COMPUTERS)
		add_notification_tasks(all_devices=all_phones, device_type=DEVICE_TYPE_PHONE, person_data_key=DATA_PHONES)
		add_notification_tasks(all_devices=all_tablets, device_type=DEVICE_TYPE_TABLET, person_data_key=DATA_TABLETS)

		# TODO: check zone and room and use those to notify lights / speakers

	await gather(*notification_tasks)


async def async_setup(hass: core.HomeAssistant, config: dict, **kwds):
	hass.data.setdefault(DOMAIN_CUSTOM_BACKEND, {})
	everpresent_actions_map = hass.data[DOMAIN_CUSTOM_BACKEND].setdefault(SHARED_EVERPRESENT_NOTIFICATION_ACTIONS, {})
	actions_map = hass.data[DOMAIN_CUSTOM_BACKEND].setdefault(SHARED_NOTIFICATION_ACTIONS, {})

	async def handle_notify(call):
		await notify(call.data, hass=hass, **kwds)

	hass.services.async_register(DOMAIN_CUSTOM_BACKEND, SERVICE_NOTIFY, handle_notify)

	async def setup_everpresent_actions():
		from custom_components.custom_backend.config.packages.garage_doors import get_garage_doors

		garage_doors = await get_garage_doors(**kwds)

		def garage_door_operation(garage_door_slug, operation):
			async def do_thing_to_garage_door(*, hass):
				await hass.services.async_call(
					DOMAIN_COVER,
					operation,
					{
						CONF_ENTITY_ID: f"{DOMAIN_COVER}.{garage_door_slug}"
					},
					blocking=True
				)
			
			return do_thing_to_garage_door

		for garage_door_slug, garage_door_data in garage_doors.items():
			everpresent_actions_map[f"{DATA_OPEN_GARAGE_DOOR}_{garage_door_slug}"] = {
				DATA_ACTION: garage_door_operation(garage_door_slug, SERVICE_OPEN_COVER),
				DATA_FULL_NAME: f"Open the {garage_door_data[DATA_FULL_NAME]}",
				DATA_REQUIRE_DEVICE_UNLOCK: True,
				DATA_SHORT_NAME: f"⬆️ {garage_door_data[DATA_NICKNAME]}",
			}

			everpresent_actions_map[f"{DATA_CLOSE_GARAGE_DOOR}_{garage_door_slug}"] = {
				DATA_ACTION: garage_door_operation(garage_door_slug, SERVICE_CLOSE_COVER),
				DATA_FULL_NAME: f"Close the {garage_door_data[DATA_FULL_NAME]}",
				DATA_REQUIRE_DEVICE_UNLOCK: False,
				DATA_SHORT_NAME: f"⬇️ {garage_door_data[DATA_NICKNAME]}",
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

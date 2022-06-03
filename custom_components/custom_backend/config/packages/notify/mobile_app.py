"Set up the mobile app notification service"

from logging import getLogger
from uuid import uuid4

from custom_components.custom_backend.const import CONF_ACTION, CONF_ACTIONS, CONF_ACTION_DATA, CONF_AUTHENTICATIONREQUIRED, CONF_CHANNEL, CONF_CLICKACTION, CONF_COLOR, CONF_CRITICAL, CONF_DATA, CONF_ENTITY_ID, CONF_GROUP, CONF_ICON_URL, CONF_IMAGE, CONF_IMPORTANCE, CONF_INTERRUPTION_LEVEL, CONF_LATITUDE, CONF_LEDCOLOR, CONF_LONGITUDE, CONF_MESSAGE, CONF_NAME, CONF_PRIORITY, CONF_PUSH, CONF_SHOWS_COMPASS, CONF_SHOWS_POINTS_OF_INTEREST, CONF_SHOWS_SCALE, CONF_SHOWS_TRAFFIC, CONF_SHOWS_USER_LOCATION, CONF_SOUND, CONF_SUBTITLE, CONF_TAG, CONF_TITLE, CONF_TTL, CONF_URL, CONF_VOLUME, DATA_ACTION, DATA_FULL_NAME, DATA_ID, DATA_LATITUDE, DATA_LONGITUDE, DATA_MOBILE_APP, DATA_REQUIRE_DEVICE_UNLOCK, DATA_SHORT_NAME, DATA_TAILWIND, DOMAIN_CAMERA, DOMAIN_CUSTOM_BACKEND, DOMAIN_NOTIFY, OS_ANDROID, OS_IOS, OS_MACOS, PRIORITY_EMERGENCY, PRIORITY_LOW, PRIORITY_NORMAL, PRIORITY_URGENT, SHARED_MEMORY_NOTIFICATION_ACTIONS
from custom_components.custom_backend.config.packages.frontend.colors import get_tailwind_2_color_palette, get_tailwind_2_gray_palette


_LOGGER = getLogger(__name__)

async def notify_mobile_app(*, actions, camera, channel, color, group, image, map, message, message_html, os, priority, push_sound, replace, slug, subtitle, title, title_html, tts, use_speaker, hass):
	all_colors = {
		**get_tailwind_2_color_palette(),
		**get_tailwind_2_gray_palette(),
	}

	if color is None:
		color = {
			DATA_TAILWIND: ["gray", 700]
		}

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

		ACTIONS_MAP = hass.data[DOMAIN_CUSTOM_BACKEND][SHARED_MEMORY_NOTIFICATION_ACTIONS]

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
		elif os in {OS_IOS, OS_MACOS}:
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

	if color is not None:
		if os == OS_ANDROID:
			[tailwind_color_name, shade] = color[DATA_TAILWIND]
			hex_code = all_colors[tailwind_color_name][shade]

			service_args[CONF_DATA][CONF_COLOR] = hex_code
			# TODO: check if channel is needed
			# if channel is not None:
			service_args[CONF_DATA][CONF_LEDCOLOR] = hex_code

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

	if priority == PRIORITY_LOW:
		if os in {OS_IOS, OS_MACOS}:
			push_config = service_args[CONF_DATA].setdefault(CONF_PUSH, {})
			push_config[CONF_INTERRUPTION_LEVEL] = "passive"
	elif priority == PRIORITY_NORMAL:
		if os in {OS_IOS, OS_MACOS}:
			push_config = service_args[CONF_DATA].setdefault(CONF_PUSH, {})
			push_config[CONF_INTERRUPTION_LEVEL] = "active"
	elif priority == PRIORITY_URGENT:
		# TODO: command_screen_on	Turn on the device screen
		if os in {OS_IOS, OS_MACOS}:
			push_config = service_args[CONF_DATA].setdefault(CONF_PUSH, {})
			push_config[CONF_INTERRUPTION_LEVEL] = "time-sensitive"
	elif priority == PRIORITY_EMERGENCY:
		if os == OS_ANDROID:
			# TODO: command_screen_on	Turn on the device screen
			service_args[CONF_DATA][CONF_PRIORITY] = "high"
			service_args[CONF_DATA][CONF_TTL] = 0
			# TODO: check if channel: alarm_stream_max works
		elif os in {OS_IOS, OS_MACOS}:
			push_config = service_args[CONF_DATA].setdefault(CONF_PUSH, {})
			push_config[CONF_INTERRUPTION_LEVEL] = "critical"
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

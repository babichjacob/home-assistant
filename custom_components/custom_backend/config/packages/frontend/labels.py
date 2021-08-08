"Created labels for the frontend"

from custom_components.custom_backend.const import (
	ATTR_ENTITY_PICTURE,
	ATTR_FRIENDLY_NAME,
	CONF_ENTITY,
	CONF_INITIAL,
	CONF_NAME,
	CONF_STATE,
	CONF_TYPE,
	DATA_FULL_NAME,
	DATA_LABEL, 
	DATA_NICKNAME, 
	DATA_IMAGE,
	DOMAIN_INPUT_TEXT,
	IMAGE_GARAGE_DOOR_CLOSED_COLOR,
	IMAGE_LIGHT_ON_COLOR,
	IMAGE_LOCK_LOCKED_COLOR,
	IMAGE_OPEN_WINDOW_COLOR,
	IMAGE_SUBWOOFER_COLOR,
	IMAGE_TV_SHOW_COLOR,
	TYPE_CUSTOM_TEMPLATE_ENTITY_ROW,
)

from custom_components.custom_backend.utils import slugify


async def get_labels(**kwds):
	labels_list = [
		# {
		# 	DATA_NICKNAME: "Active Codes",
		# 	DATA_IMAGE: IMAGE_GOOD_PINCODE_COLOR,
		# },
		# {
		# 	DATA_NICKNAME: "Call Contact",
		# 	DATA_IMAGE: IMAGE_CALL_LIST_COLOR,
		# },
		# {
		# 	DATA_NICKNAME: "Cameras",
		# 	DATA_IMAGE: IMAGE_COMPACT_CAMERA_COLOR,
		# },
		# {
		# 	DATA_NICKNAME: "Computers",
		# 	DATA_IMAGE: IMAGE_WORKSTATION_COLOR,
		# },
		{
			DATA_NICKNAME: "Garage Door",
			DATA_IMAGE: IMAGE_GARAGE_DOOR_CLOSED_COLOR,
		},
		# {
		# 	DATA_NICKNAME: "Generate New Code",
		# 	DATA_IMAGE: IMAGE_KEYPAD_COLOR,
		# },
		# {
		# 	DATA_NICKNAME: "Internet Blocking",
		# 	DATA_IMAGE: IMAGE_WEB_SHIELD_COLOR,
		# },
		# {
		# 	DATA_NICKNAME: "Jacob's Computer",
		# 	DATA_IMAGE: IMAGE_WORKSTATION_COLOR,
		# },
		{
			DATA_NICKNAME: "Lights",
			DATA_IMAGE: IMAGE_LIGHT_ON_COLOR,
		},
		{
			DATA_NICKNAME: "Locks",
			DATA_IMAGE: IMAGE_LOCK_LOCKED_COLOR,
		},
		# {
		# 	DATA_NICKNAME: "Map",
		# 	DATA_IMAGE: IMAGE_PLACE_MARKER_COLOR,
		# },
		# {
		# 	DATA_NICKNAME: "Offline Devices",
		# 	DATA_IMAGE: IMAGE_OFFLINE_COLOR,
		# },
		# {
		# 	DATA_NICKNAME: "People",
		# 	DATA_IMAGE: IMAGE_TEAM_COLOR,
		# },
		# {
		# 	DATA_NICKNAME: "Security",
		# 	DATA_IMAGE: IMAGE_DEFENSE_COLOR,
		# },
		# {
		# 	DATA_NICKNAME: "Shopping List",
		# 	DATA_IMAGE: IMAGE_LIST_VIEW_COLOR,
		# },
		# {
		# 	DATA_NICKNAME: "Smoke Detector",
		# 	DATA_IMAGE: IMAGE_SENSOR_COLOR,
		# },
		{
			DATA_NICKNAME: "Speakers",
			DATA_IMAGE: IMAGE_SUBWOOFER_COLOR,
		},
		# {
		# 	DATA_NICKNAME: "The Katniss Server",
		# 	DATA_IMAGE: IMAGE_ROOT_SERVER_COLOR,
		# },
		{
			DATA_NICKNAME: "TVs",
			DATA_IMAGE: IMAGE_TV_SHOW_COLOR,
		},
		# {
		# 	DATA_NICKNAME: "Use the Wyze app",
		# 	DATA_IMAGE: IMAGE_WYZE_LOGO,
		# },
		# {
		# 	DATA_NICKNAME: "Weather & Thermostat",
		# 	DATA_IMAGE: IMAGE_STORMY_WEATHER_COLOR,
		# },
		{
			DATA_NICKNAME: "Windows",
			DATA_IMAGE: IMAGE_OPEN_WINDOW_COLOR,
		},
	]

	labels = {
		slugify(label_data[DATA_NICKNAME]): label_data for label_data in labels_list
	}

	for label_data in labels.values():
		label_data.setdefault(DATA_FULL_NAME, f'"{label_data[DATA_NICKNAME]}" Label')

	return labels


async def get_label_lovelace_element(*, nickname, **kwds):
	labels = await get_labels(**kwds)

	label_slug = next(label_slug for label_slug, label_data in labels.items() if label_data[DATA_NICKNAME] == nickname)

	label_data = labels[label_slug]

	return {
		CONF_TYPE: TYPE_CUSTOM_TEMPLATE_ENTITY_ROW,
		CONF_ENTITY: f"{DOMAIN_INPUT_TEXT}.{label_slug}_{DATA_LABEL}",
		CONF_NAME: label_data[DATA_NICKNAME],
		CONF_STATE: " ",
	}


async def generate_yaml(**kwds):
	labels = await get_labels(**kwds)

	label_input_texts = {
		f"{label_slug}_{DATA_LABEL}": {
			CONF_INITIAL: label_data[DATA_NICKNAME],
			CONF_NAME: label_data[DATA_FULL_NAME],
		} for label_slug, label_data in labels.items()
	}

	return {
		DOMAIN_INPUT_TEXT: label_input_texts,
	}


async def customize(**kwds):
	labels = await get_labels(**kwds)

	customize_label_input_texts = {
		f"{DOMAIN_INPUT_TEXT}.{label_slug}_{DATA_LABEL}": {
			ATTR_ENTITY_PICTURE: label_data[DATA_IMAGE],
		} for label_slug, label_data in labels.items()
	}

	return {
		**customize_label_input_texts
	}

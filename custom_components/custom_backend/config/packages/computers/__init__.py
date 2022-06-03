"Registered all the computers with the home automation and security system"


from custom_components.custom_backend.const import ATTR_ENTITY_PICTURE, ATTR_FRIENDLY_NAME, ATTR_ICON, BROWSER_CHROME, BROWSER_FIREFOX, BROWSER_MOBILE_APP, COMPUTER_JACOB_S_DESKTOP, COMPUTER_JACOB_S_SCHOOL_LAPTOP, CONF_ENTITIES, CONF_INCLUDE, DATA_BROWSERS, DATA_BROWSER_MOD, DATA_SECRETS, DEVICE_TYPE_COMPUTER, DATA_FULL_NAME, DATA_NICKNAME, DATA_OSES, DEVICE_TYPE_PHONE, DATA_PHOTO, DATA_SLUG, DEVICE_TYPE_TABLET, DOMAIN_DEVICE_TRACKER, DOMAIN_RECORDER, DOMAIN_SENSOR, DOMAIN_LIGHT, DOMAIN_MEDIA_PLAYER, ICON_MDI_CELLPHONE, ICON_MDI_CELLPHONE_SOUND, ICON_MDI_CELLPHONE_TEXT, ICON_MDI_MONITOR_DASHBOARD, ICON_MDI_MONITOR_EYE, ICON_MDI_MONITOR_SPEAKER, ICON_MDI_TABLET, ICON_MDI_TABLET_DASHBOARD, OS_MACOS, OS_WINDOWS
from custom_components.custom_backend.utils import slugify


# TODO: identify loose browser_mod device id e5fe0b23-15a106e2
async def get_computers(**kwds):
	computers = {
		COMPUTER_JACOB_S_DESKTOP: {
			DATA_NICKNAME: "Jacob's Desktop",
			DATA_OSES: {
				OS_MACOS: {
					DATA_BROWSERS: {
						BROWSER_CHROME: {
							DATA_BROWSER_MOD: "7abcadab-b52fc99f",
						},
						BROWSER_FIREFOX: {
							DATA_BROWSER_MOD: "aa0c9f87-c05b07de",
						},
						BROWSER_MOBILE_APP: {
							DATA_BROWSER_MOD: "cde4b429-dc9e972e",
							DATA_SLUG: "jacobs_mac_pro",
						},
					}
				},
				OS_WINDOWS: {
					DATA_BROWSERS: {
						BROWSER_CHROME: {
							DATA_BROWSER_MOD: "f6c8d040-f71baebb",
						},
					},
				},
			},
		},
		COMPUTER_JACOB_S_SCHOOL_LAPTOP: {
			DATA_NICKNAME: "Jacob's School Laptop",
			DATA_OSES: {
				OS_WINDOWS: {
					DATA_BROWSERS: {
						BROWSER_CHROME: {
							DATA_BROWSER_MOD: "73977112-42a4b5ef",
						},
						BROWSER_FIREFOX: {
							DATA_BROWSER_MOD: "39849e3d-123aba1d",
						},
					}
				},
			},
		},
	}

	for computer_slug, computer_data in computers.items():
		computer_data.setdefault(DATA_FULL_NAME, f"{computer_data[DATA_NICKNAME]} Computer")
		computer_data.setdefault(DATA_PHOTO, f"/local/device/{computer_slug}.png")

	return computers


def get_customize_for_browser_mod(devices, *, device_type):
	customizations = {}

	for device_slug, device_data in devices.items():
		device_name = device_data[DATA_FULL_NAME]

		for os_name, os_data in device_data[DATA_OSES].items():
			is_only_os = len(device_data[DATA_OSES]) == 1

			for browser_name, browser_data in os_data[DATA_BROWSERS].items():
				is_only_browser = len(os_data[DATA_BROWSERS]) == 1

				device_id = browser_data[DATA_BROWSER_MOD]

				friendly_name = device_name
				if not is_only_os:
					friendly_name = f"{friendly_name}'s {os_name} Installation"
				if not is_only_browser:
					friendly_name = f"{friendly_name}'s {browser_name}"

				dashboard_visible_icons = {
					DEVICE_TYPE_COMPUTER: ICON_MDI_MONITOR_DASHBOARD,
					DEVICE_TYPE_PHONE: ICON_MDI_CELLPHONE_TEXT,
					DEVICE_TYPE_TABLET: ICON_MDI_TABLET_DASHBOARD,
				}
				customizations[f"{DOMAIN_LIGHT}.{slugify(device_id)}"] = {
					ATTR_FRIENDLY_NAME: f"{friendly_name} Home Assistant View Not Blacked Out",
					ATTR_ICON: dashboard_visible_icons[device_type],
				}

				audio_receiver_icons = {
					DEVICE_TYPE_COMPUTER: ICON_MDI_MONITOR_SPEAKER,
					DEVICE_TYPE_PHONE: ICON_MDI_CELLPHONE_SOUND,
					DEVICE_TYPE_TABLET: ICON_MDI_CELLPHONE_SOUND,
				}
				customizations[f"{DOMAIN_MEDIA_PLAYER}.{slugify(device_id)}"] = {
					ATTR_FRIENDLY_NAME: f"{friendly_name} Home Assistant View Audio Receiver",
					ATTR_ICON: audio_receiver_icons[device_type],
				}

				view_icons = {
					DEVICE_TYPE_COMPUTER: ICON_MDI_MONITOR_EYE,
					DEVICE_TYPE_PHONE: ICON_MDI_CELLPHONE,
					DEVICE_TYPE_TABLET: ICON_MDI_TABLET,
				}
				customizations[f"{DOMAIN_SENSOR}.{slugify(device_id)}"] = {
					ATTR_FRIENDLY_NAME: f"{friendly_name} Home Assistant View",
					ATTR_ICON: view_icons[device_type],
				}
	
	return customizations


def get_customize_for_mobile_app(devices):
	return {
		f"{DOMAIN_DEVICE_TRACKER}.{browser_data[DATA_SLUG]}": {
			ATTR_ENTITY_PICTURE: device_data[DATA_PHOTO],
			ATTR_FRIENDLY_NAME: f"{device_data[DATA_FULL_NAME]} {os_name} Mobile App Location",
		} for device_data in devices.values() for os_name, os_data in device_data[DATA_OSES].items() for browser_name, browser_data in os_data[DATA_BROWSERS].items() if browser_name == BROWSER_MOBILE_APP
	}


def add_gps_device_trackers_to_recorder(devices):
	return {
		DOMAIN_RECORDER: {
			CONF_INCLUDE: {
				CONF_ENTITIES: [f"{DOMAIN_DEVICE_TRACKER}.{browser_data[DATA_SLUG]}" for device_data in devices.values() for os_name, os_data in device_data[DATA_OSES].items() for browser_name, browser_data in os_data[DATA_BROWSERS].items() if browser_name == BROWSER_MOBILE_APP]
			}
		}
	}


async def generate_yaml(**kwds):
	computers = await get_computers(**kwds)

	return {
		**add_gps_device_trackers_to_recorder(computers),
	}


async def customize(**kwds):
	computers = await get_computers(**kwds)

	return {
		**get_customize_for_browser_mod(computers, device_type=DEVICE_TYPE_COMPUTER),
		**get_customize_for_mobile_app(computers),
	}

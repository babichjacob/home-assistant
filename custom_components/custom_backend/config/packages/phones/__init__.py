"Registered all the phones with the home automation and security system"

from custom_components.custom_backend.const import ATTR_ENTITY_PICTURE, ATTR_FRIENDLY_NAME, ATTR_ICON, BROWSER_CHROME, BROWSER_FIREFOX, BROWSER_MOBILE_APP, DATA_BROWSERS, DATA_BROWSER_MOD, DATA_DEVICE_ID, DATA_FULL_NAME, DATA_ICON, DATA_ID, DATA_NICKNAME, DATA_OS, DATA_OSES, DATA_PHONE, DATA_PHOTO, DATA_SLUG, DATA_UNIFI_DEVICE_TRACKER_SLUG, DOMAIN_DEVICE_TRACKER, ICON_MDI_CELLPHONE, OS_ANDROID, OS_IOS, PHONE_GALAXY_S21_ULTRA_1, PHONE_GLORIA_S_IPHONE_XR, PHONE_JACOB_S_HTC_U11, PHONE_JENNA_S_IPHONE_XR, PHONE_MATT_S_ONEPLUS_8, ZONE_BAKA_S_HOUSE
from custom_components.custom_backend.utils import slugify


from custom_components.custom_backend.config.packages.computers import add_gps_device_trackers_to_recorder, get_customize_for_browser_mod, get_customize_for_mobile_app


async def get_phones(**kwds):
	phones = {
		PHONE_GALAXY_S21_ULTRA_1: {
			DATA_FULL_NAME: "Jacob's Galaxy S21 Ultra",
			# DATA_ICON: ICON_MDI_CELLPHONE_ANDROID,
			DATA_NICKNAME: "Jacob's Galaxy S21 Ultra",
			DATA_OSES: {
				OS_ANDROID: {
					DATA_BROWSERS: {
						BROWSER_MOBILE_APP: {
							DATA_BROWSER_MOD: "70d3b9b7-0f490671",
							DATA_DEVICE_ID: "81a91a5eb6b82bae",
							DATA_SLUG: "galaxy_s21_ultra_1",
						},
					},
				},
			},
			DATA_UNIFI_DEVICE_TRACKER_SLUG: "jacob_s_s21_ultra",
		},
		PHONE_GLORIA_S_IPHONE_XR: {
			DATA_FULL_NAME: "Gloria's iPhone XR",
			# DATA_ICON: ICON_MDI_CELLPHONE_IPHONE,
			DATA_NICKNAME: "Gloria's iPhone XR",
			DATA_OSES: {
				OS_IOS: {
					DATA_BROWSERS: {},
				},
			},
			DATA_UNIFI_DEVICE_TRACKER_SLUG: "phone_gloria",
		},
		PHONE_JACOB_S_HTC_U11: {
			DATA_FULL_NAME: "Jacob's HTC U11",
			# DATA_ICON: ICON_MDI_CELLPHONE_ANDROID,
			DATA_NICKNAME: "Jacob's HTC U11",
			DATA_OSES: {
				OS_ANDROID: {
					DATA_BROWSERS: {
						BROWSER_CHROME: {
							DATA_BROWSER_MOD: "ce9e4cfe-8110b4a8",
						},
						BROWSER_MOBILE_APP: {
							DATA_BROWSER_MOD: "cab9a43c-ec5e13ae",
							DATA_DEVICE_ID: "62eecd9375cd71b8",
							DATA_SLUG: "jacob_s_htc_u11_with_sense",
						},
					}
				},
			},
			DATA_UNIFI_DEVICE_TRACKER_SLUG: "phone_jacob_s_htc_u11",
		},
		PHONE_JENNA_S_IPHONE_XR: {
			DATA_FULL_NAME: "Jenna's iPhone XR",
			# DATA_ICON: ICON_MDI_CELLPHONE_IPHONE,
			DATA_NICKNAME: "Jenna's iPhone XR",
			DATA_OSES: {
				OS_IOS: {
					DATA_BROWSERS: {
						BROWSER_MOBILE_APP: {
							DATA_BROWSER_MOD: "ab85e81d-cfeaf2bc",
							DATA_DEVICE_ID: "6ACE2E98-BCD3-4CDE-9314-F279850EEAF1",
							DATA_SLUG: "iphone",
						}
					}
				}
			},
			DATA_UNIFI_DEVICE_TRACKER_SLUG: "iphone_2",
		},
		PHONE_MATT_S_ONEPLUS_8: {
			DATA_FULL_NAME: "Matt's OnePlus 8",
			# DATA_ICON: ICON_MDI_CELLPHONE_ANDROID,
			DATA_NICKNAME: "Matt's OnePlus 8",
			DATA_OSES: {
				OS_ANDROID: {
					DATA_BROWSERS: {
						BROWSER_MOBILE_APP: {
							DATA_BROWSER_MOD: "d93f0896-afdf9333",
							DATA_DEVICE_ID: "fd553540be0b6e89",
							DATA_SLUG: "matt_s_oneplus_8",
						},
					}
				},
			},
			DATA_UNIFI_DEVICE_TRACKER_SLUG: "phone_matt_s_oneplus_8",
		},
	}

	for phone_slug, phone_data in phones.items():
		phone_data.setdefault(DATA_FULL_NAME, f"{phone_data[DATA_NICKNAME]} Phone")
		phone_data.setdefault(DATA_ICON, ICON_MDI_CELLPHONE)
		phone_data.setdefault(DATA_PHOTO, f"/local/device/{phone_slug}.png")

	return phones


async def generate_yaml(**kwds):
	phones = await get_phones(**kwds)

	return {
		**add_gps_device_trackers_to_recorder(phones),
	}


async def customize(**kwds):
	phones = await get_phones(**kwds)

	customize_unifi_device_trackers = {
		f"{DOMAIN_DEVICE_TRACKER}.{phone_data[DATA_UNIFI_DEVICE_TRACKER_SLUG]}": {
			ATTR_ENTITY_PICTURE: phone_data[DATA_PHOTO],
			ATTR_FRIENDLY_NAME: f"{phone_data[DATA_FULL_NAME]} Connected to Internet at {ZONE_BAKA_S_HOUSE}",
			ATTR_ICON: phone_data[DATA_ICON],
		} for phone_data in phones.values()
	}

	return {
		**customize_unifi_device_trackers,
		**get_customize_for_browser_mod(phones, device_type=DATA_PHONE),
		**get_customize_for_mobile_app(phones),
	}

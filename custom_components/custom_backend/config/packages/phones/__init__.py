"Registered all the phones with the home automation and security system"

from custom_components.custom_backend.const import ATTR_FRIENDLY_NAME, ATTR_ICON, BROWSER_CHROME, BROWSER_FIREFOX, BROWSER_MOBILE_APP, DATA_BROWSERS, DATA_BROWSER_MOD, DATA_FULL_NAME, DATA_NICKNAME, DATA_OS, DATA_OSES, DATA_PHONE, DATA_PHOTO, DATA_SLUG, DOMAIN_SENSOR, DOMAIN_LIGHT, DOMAIN_MEDIA_PLAYER, OS_ANDROID, OS_IOS, OS_MACOS, PHONE_JACOB_S_HTC_U11, PHONE_JENNA_S_IPHONE_XR, PHONE_MATT_S_ONEPLUS_8
from custom_components.custom_backend.utils import slugify


from custom_components.custom_backend.config.packages.computers import add_device_trackers_to_recorder, get_customize_for_browser_mod, get_customize_for_mobile_app


async def get_phones(**kwds):
	phones = {
		PHONE_JACOB_S_HTC_U11: {
			DATA_FULL_NAME: "Jacob's HTC U11",
			DATA_NICKNAME: "Jacob's HTC U11",
			DATA_OSES: {
				OS_ANDROID: {
					DATA_BROWSERS: {
						BROWSER_CHROME: {
							DATA_BROWSER_MOD: "ce9e4cfe-8110b4a8",
						},
						BROWSER_MOBILE_APP: {
							DATA_BROWSER_MOD: "cab9a43c-ec5e13ae",
							DATA_SLUG: "jacob_s_htc_u11_with_sense",
						},
					}
				},
			},
		},
		PHONE_JENNA_S_IPHONE_XR: {
			DATA_FULL_NAME: "Jenna's iPhone XR",
			DATA_NICKNAME: "Jenna's iPhone XR",
			DATA_OSES: {
				OS_IOS: {
					DATA_BROWSERS: {
						BROWSER_MOBILE_APP: {
							DATA_BROWSER_MOD: "ab85e81d-cfeaf2bc",
							DATA_SLUG: "iphone",
						}
					}
				}
			}
		},
		PHONE_MATT_S_ONEPLUS_8: {
			DATA_FULL_NAME: "Matt's OnePlus 8",
			DATA_NICKNAME: "Matt's OnePlus 8",
			DATA_OSES: {
				OS_ANDROID: {
					DATA_BROWSERS: {
						BROWSER_MOBILE_APP: {
							DATA_BROWSER_MOD: "d93f0896-afdf9333",
							DATA_SLUG: "matt_s_oneplus_8",
						},
					}
				},
			},
		},
	}

	for phone_slug, phone_data in phones.items():
		phone_data.setdefault(DATA_FULL_NAME, f"{phone_data[DATA_NICKNAME]} Phone")
		phone_data.setdefault(DATA_PHOTO, f"/local/device/{phone_slug}.png")

	return phones


async def generate_yaml(**kwds):
	phones = await get_phones(**kwds)

	return {
		**add_device_trackers_to_recorder(phones),
	}


async def customize(**kwds):
	phones = await get_phones(**kwds)

	return {
		**get_customize_for_browser_mod(phones, device_type=DATA_PHONE),
		**get_customize_for_mobile_app(phones),
	}

"Registered all the tablets with the home automation and security system"


from custom_components.custom_backend.const import BROWSER_MOBILE_APP, DATA_BROWSERS, DATA_BROWSER_MOD, DATA_FULL_NAME, DATA_NICKNAME, DATA_OSES, DATA_PHOTO, DATA_SLUG, DEVICE_TYPE_TABLET, OS_IOS, TABLET_MATT_S_2015_IPAD_PRO
from custom_components.custom_backend.config.packages.computers import add_device_trackers_to_recorder, get_customize_for_browser_mod, get_customize_for_mobile_app


async def get_tablets(**kwds):
	tablets = {
		TABLET_MATT_S_2015_IPAD_PRO: {
			DATA_NICKNAME: "Matt's 2015 iPad Pro",
			DATA_FULL_NAME: "Matt's 2015 iPad Pro",
			DATA_OSES: {
				OS_IOS: {
					DATA_BROWSERS: {
						BROWSER_MOBILE_APP: {
							DATA_BROWSER_MOD: "fbc6c796-ed68a55d",
							DATA_SLUG: "matts_ipad_pro",
						},
					}
				},
			},
		},
	}

	for tablet_slug, tablet_data in tablets.items():
		tablet_data.setdefault(DATA_FULL_NAME, f"{tablet_data[DATA_NICKNAME]} Tablet")
		tablet_data.setdefault(DATA_PHOTO, f"/local/device/{tablet_slug}.png")

	return tablets


async def generate_yaml(**kwds):
	tablets = await get_tablets(**kwds)

	return {
		**add_device_trackers_to_recorder(tablets),
	}


async def customize(**kwds):
	tablets = await get_tablets(**kwds)

	return {
		**get_customize_for_browser_mod(tablets, device_type=DEVICE_TYPE_TABLET),
		**get_customize_for_mobile_app(tablets),
	}

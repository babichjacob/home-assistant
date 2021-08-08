"Registered TVs with the security system"

from custom_components.custom_backend.const import (
	ATTR_DEVICE_CLASS,
	ATTR_FRIENDLY_NAME,
	ATTR_ICON,
	DATA_CHROMECAST,
	DATA_FULL_NAME,
	DATA_HOST,
	DATA_COMES_FROM_ROKU,
	DATA_ICON,
	DATA_IS_TV,
	DATA_NICKNAME,
	DATA_ROKU,
	DATA_ROOM,
	DATA_SHORT_NAME,
	DATA_ZONE,
	DEVICE_CLASS_TV,
	DOMAIN_MEDIA_PLAYER,
	DOMAIN_REMOTE,
	ICON_MDI_REMOVE_TV,
	ICON_MDI_TELEVISION,
	ROOM_BAKA_S_BEDROOM,
	ROOM_BASEMENT,
	ROOM_FRONT_ROOM,
	ROOM_JACOB_S_BEDROOM,
	ROOM_JENNA_S_BEDROOM,
	ROOM_KITCHEN,
	ROOM_MATT_S_BEDROOM,
	ZONE_BAKA_S_HOUSE,
)

async def get_tvs(**kwds):
	secrets = kwds["secrets"]

	tvs = {
		"baka_s_bedroom": {
			DATA_ROKU: {
				DATA_COMES_FROM_ROKU: "43_tcl_roku_tv",
				DATA_HOST: secrets["roku_2_host"],
				DATA_IS_TV: True,
			},
			DATA_ROOM: ROOM_BAKA_S_BEDROOM,
		},
		"basement": {
			DATA_CHROMECAST: "basement_chromecast",
			DATA_ROKU: {
				DATA_COMES_FROM_ROKU: "49_inch_roku_tv",
				DATA_HOST: secrets["roku_1_host"],
				DATA_IS_TV: True,
			},
			DATA_ROOM: ROOM_BASEMENT,
		},
		"fireplace": {
			DATA_CHROMECAST: "matt_s_chromecast",
			DATA_NICKNAME: "Fireplace",
			DATA_ROKU: {
				DATA_COMES_FROM_ROKU: "roku_streaming_stick_2",
				DATA_HOST: secrets["roku_7_host"],
				DATA_IS_TV: False,
			},
			DATA_ROOM: ROOM_KITCHEN,
		},
		"front_room": {
			DATA_CHROMECAST: "chromecast_ultra",
			DATA_ROKU: {
				DATA_COMES_FROM_ROKU: "55_inch_roku_tv",
				DATA_HOST: secrets["roku_3_host"],
				DATA_IS_TV: True,
			},
			DATA_ROOM: ROOM_FRONT_ROOM,
		},
		"jacob_s_bedroom": {
			DATA_ROKU: {
				DATA_COMES_FROM_ROKU: "jacob_s_roku",
				DATA_HOST: secrets["roku_4_host"],
				DATA_IS_TV: True,
			},
			DATA_ROOM: ROOM_JACOB_S_BEDROOM,
		},
		"jenna_s_bedroom": {
			DATA_ROKU: {
				DATA_COMES_FROM_ROKU: "jenna_s_roku_streaming_stick",
				DATA_HOST: secrets["roku_5_host"],
				DATA_IS_TV: False,
			},
			DATA_ROOM: ROOM_JENNA_S_BEDROOM,
		},
		"matt_s_bedroom": {
			DATA_ROKU: {
				DATA_COMES_FROM_ROKU: "matt_s_roku_streaming_stick",
				DATA_HOST: secrets["roku_6_host"],
				DATA_IS_TV: False,
			},
			DATA_ROOM: ROOM_MATT_S_BEDROOM,
		},
	}

	for tv_data in tvs.values():
		tv_data.setdefault(DATA_ROKU, {})
		tv_data[DATA_ROKU].setdefault(DATA_IS_TV, False)
		
		tv_data.setdefault(DATA_CHROMECAST, None)
		tv_data.setdefault(DATA_NICKNAME, tv_data[DATA_ROOM])
		tv_data.setdefault(DATA_FULL_NAME, f"{tv_data[DATA_NICKNAME]} TV")
		tv_data.setdefault(DATA_ICON, ICON_MDI_TELEVISION)
		tv_data.setdefault(DATA_SHORT_NAME, "TV")
		tv_data.setdefault(DATA_ZONE, ZONE_BAKA_S_HOUSE)

	return tvs


async def customize(**kwds):
	tvs = await get_tvs(**kwds)

	connected_chromecasts = {
		f"{DOMAIN_MEDIA_PLAYER}.{tv_data[DATA_CHROMECAST]}": {
			ATTR_FRIENDLY_NAME: f"{tv_data[DATA_NICKNAME]} Chromecast",
		} for tv_data in tvs.values() if tv_data[DATA_CHROMECAST] is not None
	}

	roku_media_players = {
		f"{DOMAIN_MEDIA_PLAYER}.{tv_data[DATA_ROKU][DATA_COMES_FROM_ROKU]}": {
			ATTR_DEVICE_CLASS: DEVICE_CLASS_TV,
			ATTR_FRIENDLY_NAME: tv_data[DATA_FULL_NAME],
			ATTR_ICON: tv_data[DATA_ICON],
		} for tv_data in tvs.values()
	}

	roku_remotes = {
		f"{DOMAIN_REMOTE}.{tv_data[DATA_ROKU][DATA_COMES_FROM_ROKU]}": {
			ATTR_FRIENDLY_NAME: f"{tv_data[DATA_FULL_NAME]} Remote",
			ATTR_ICON: ICON_MDI_REMOVE_TV,
		} for tv_data in tvs.values()
	}

	return {
		**connected_chromecasts,
		**roku_media_players,
		**roku_remotes,
	}


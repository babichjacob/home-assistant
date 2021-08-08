"Registered speakers with the security system"

from custom_components.custom_backend.const import (
	ATTR_DEVICE_CLASS,
	ATTR_FRIENDLY_NAME,
	ATTR_ICON,
	DATA_CHROMECAST,
	DATA_FULL_NAME,
	DATA_GROUP_MEMBERS,
	DATA_HAS_DISPLAY,
	DATA_ICON,
	DATA_NICKNAME,
	DATA_ROOM,
	DATA_SHORT_NAME,
	DATA_ZONE,
	DEVICE_CLASS_SPEAKER,
	DOMAIN_MEDIA_PLAYER,
	ICON_MDI_SPEAKER,
	ICON_MDI_SPEAKER_MULTIPLE,
	ICON_MDX_GOOGLE_HOME_MINI,
	ICON_MDX_LENOVO_SMART_DISPLAY,
	ROOM_BASEMENT,
	ROOM_BATHROOM,
	ROOM_FRONT_ROOM,
	ROOM_JACOB_S_BEDROOM,
	ROOM_KITCHEN,
	ROOM_MATT_S_BEDROOM,
	ZONE_BAKA_S_HOUSE
)

async def get_speakers(**kwds):
	speakers = {
		"basement": {
			DATA_CHROMECAST: "basement_display",
			DATA_ICON: ICON_MDX_LENOVO_SMART_DISPLAY,
			DATA_ROOM: ROOM_BASEMENT,
			DATA_HAS_DISPLAY: True,
		},
		"bathroom": {
			DATA_CHROMECAST: "bathroom_speaker",
			DATA_ICON: ICON_MDI_SPEAKER,
			DATA_ROOM: ROOM_BATHROOM,
			DATA_HAS_DISPLAY: False,
		},
		"front_room": {
			DATA_CHROMECAST: "front_room_display",
			DATA_ICON: ICON_MDX_LENOVO_SMART_DISPLAY,
			DATA_ROOM: ROOM_FRONT_ROOM,
			DATA_HAS_DISPLAY: True,
		},
		"jacob_s_bedroom": {
			DATA_CHROMECAST: "jacob_s_bedroom_speaker",
			DATA_ICON: ICON_MDI_SPEAKER,
			DATA_ROOM: ROOM_JACOB_S_BEDROOM,
			DATA_HAS_DISPLAY: False,
		},
		"kitchen": {
			DATA_CHROMECAST: "kitchen_display",
			DATA_ICON: ICON_MDX_LENOVO_SMART_DISPLAY,
			DATA_ROOM: ROOM_KITCHEN,
			DATA_HAS_DISPLAY: True,
		},
		"matt_s_bedroom": {
			DATA_CHROMECAST: "matt_s_home_mini",
			DATA_ICON: ICON_MDX_GOOGLE_HOME_MINI,
			DATA_ROOM: ROOM_MATT_S_BEDROOM,
			DATA_HAS_DISPLAY: False,
		},
	}

	for speaker_data in speakers.values():
		speaker_data.setdefault(DATA_HAS_DISPLAY, False)
		speaker_data.setdefault(DATA_ICON, ICON_MDI_SPEAKER)
		speaker_data.setdefault(DATA_NICKNAME, f"{speaker_data[DATA_ROOM]}")
		speaker_data.setdefault(DATA_FULL_NAME, f"{speaker_data[DATA_NICKNAME]} Speaker")
		speaker_data.setdefault(DATA_SHORT_NAME, "Speaker")
		speaker_data.setdefault(DATA_ZONE, ZONE_BAKA_S_HOUSE)

	return speakers


async def get_speakers_groups(**kwds):
	speakers = await get_speakers(**kwds)

	speaker_groups = {
		"front_room_and_kitchen": {
			DATA_CHROMECAST: "front_room_and_kitchen",
			DATA_GROUP_MEMBERS: ["front_room", "kitchen"],
		},
		"ground_floor": {
			DATA_CHROMECAST: "ground_floor_speakers",
			DATA_GROUP_MEMBERS: ["bathroom", "front_room", "jacob_s_bedroom", "kitchen"],
			DATA_NICKNAME: "Ground Floor",
		},
	}

	for speaker_group_data in speaker_groups.values():
		speaker_group_data.setdefault(DATA_ICON, ICON_MDI_SPEAKER_MULTIPLE)

		if DATA_NICKNAME not in speaker_group_data:
			[*commas, second_last, last] = speaker_group_data[DATA_GROUP_MEMBERS]
			speaker_group_data[DATA_NICKNAME] = speakers[second_last][DATA_NICKNAME] + (", and " if commas else " and ") + speakers[last][DATA_NICKNAME]
			if commas:
				speaker_group_data[DATA_NICKNAME] = ", ".join(speakers[speaker_slug][DATA_NICKNAME] for speaker_slug in commas) + ", " + speaker_group_data[DATA_NICKNAME]

		speaker_group_data.setdefault(DATA_FULL_NAME, f"{speaker_group_data[DATA_NICKNAME]} Speakers")

	return speaker_groups


async def customize(**kwds):
	speakers = await get_speakers(**kwds)
	speaker_groups = await get_speakers_groups(**kwds)

	speaker_media_players = {
		f"{DOMAIN_MEDIA_PLAYER}.{speaker_data[DATA_CHROMECAST]}": {
			ATTR_DEVICE_CLASS: DEVICE_CLASS_SPEAKER,
			ATTR_FRIENDLY_NAME: speaker_data[DATA_FULL_NAME],
			ATTR_ICON: speaker_data[DATA_ICON],
		} for speaker_data in speakers.values()
	}

	speaker_group_media_players = {
		f"{DOMAIN_MEDIA_PLAYER}.{speaker_group_data[DATA_CHROMECAST]}": {
			ATTR_DEVICE_CLASS: DEVICE_CLASS_SPEAKER,
			ATTR_FRIENDLY_NAME: speaker_group_data[DATA_FULL_NAME],
			ATTR_ICON: speaker_group_data[DATA_ICON],
		} for speaker_group_data in speaker_groups.values()
	}

	return {
		**speaker_media_players,
		**speaker_group_media_players,
	}

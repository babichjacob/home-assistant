"Registered speakers with the security system"

from custom_components.custom_backend.const import (
	ATTR_DEVICE_CLASS,
	ATTR_ENTITY_PICTURE,
	ATTR_FRIENDLY_NAME,
	ATTR_ICON,
	DATA_CHROMECAST,
	DATA_FULL_NAME,
	DATA_GROUP_MEMBERS,
	DATA_HAS_DISPLAY,
	DATA_ICON,
	DATA_IMAGE,
	DATA_IS_INTEGRATED,
	DATA_NICKNAME,
	DATA_ROOM,
	DATA_SHORT_NAME,
	DATA_SLUG,
	DATA_UNIFI_DEVICE_TRACKER_SLUG,
	DATA_ZONE,
	DEVICE_CLASS_SPEAKER,
	DOMAIN_DEVICE_TRACKER,
	DOMAIN_MEDIA_PLAYER,
	ICON_MDI_CAST_AUDIO,
	ICON_MDI_SPEAKER,
	ICON_MDI_SPEAKER_MULTIPLE,
	ICON_MDX_GOOGLE_HOME_MINI,
	ICON_MDX_LENOVO_SMART_DISPLAY,
	IMAGE_GOOGLE_ASSISTANT_TRANSPARENT_LOGO,
	ROOM_BAKA_S_BEDROOM,
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
			DATA_CHROMECAST: {
				DATA_SLUG: "basement_display",
				DATA_UNIFI_DEVICE_TRACKER_SLUG: "display_basement",
			},
			DATA_ICON: ICON_MDX_LENOVO_SMART_DISPLAY,
			DATA_ROOM: ROOM_JACOB_S_BEDROOM,
			DATA_HAS_DISPLAY: True,
		},
		"bathroom": {
			DATA_CHROMECAST: {
				DATA_SLUG: "bathroom_speaker",
				DATA_UNIFI_DEVICE_TRACKER_SLUG: "speaker_bathroom",
			},
			DATA_ICON: ICON_MDI_SPEAKER,
			DATA_IMAGE: IMAGE_GOOGLE_ASSISTANT_TRANSPARENT_LOGO,
			DATA_ROOM: ROOM_BATHROOM,
			DATA_HAS_DISPLAY: False,
		},
		"front_room": {
			DATA_CHROMECAST: {
				DATA_SLUG: "front_room_display",
				DATA_UNIFI_DEVICE_TRACKER_SLUG: "display_front_room",
			},
			DATA_ICON: ICON_MDX_LENOVO_SMART_DISPLAY,
			DATA_ROOM: ROOM_FRONT_ROOM,
			DATA_HAS_DISPLAY: True,
		},
		"jacob_s_bedroom": {
			DATA_CHROMECAST: {
				DATA_SLUG: "jacob_s_bedroom_speaker",
				DATA_UNIFI_DEVICE_TRACKER_SLUG: "speaker_baka",
			},
			DATA_ICON: ICON_MDI_SPEAKER,
			DATA_IMAGE: IMAGE_GOOGLE_ASSISTANT_TRANSPARENT_LOGO,
			DATA_ROOM: ROOM_BAKA_S_BEDROOM,
			DATA_HAS_DISPLAY: False,
		},
		"kitchen": {
			DATA_CHROMECAST: {
				DATA_SLUG: "kitchen_display",
				DATA_UNIFI_DEVICE_TRACKER_SLUG: "display_kitchen",
			},
			DATA_ICON: ICON_MDX_LENOVO_SMART_DISPLAY,
			DATA_ROOM: ROOM_KITCHEN,
			DATA_HAS_DISPLAY: True,
		},
		"matt_s_bedroom": {
			DATA_CHROMECAST: {
				DATA_SLUG: "matt_s_home_mini",
				DATA_UNIFI_DEVICE_TRACKER_SLUG: "speaker_matt",
			},
			DATA_ICON: ICON_MDX_GOOGLE_HOME_MINI,
			DATA_IMAGE: IMAGE_GOOGLE_ASSISTANT_TRANSPARENT_LOGO,
			DATA_ROOM: ROOM_MATT_S_BEDROOM,
			DATA_HAS_DISPLAY: False,
		},
	}

	for speaker_data in speakers.values():
		speaker_data.setdefault(DATA_HAS_DISPLAY, False)
		speaker_data.setdefault(DATA_ICON, ICON_MDI_SPEAKER)
		speaker_data.setdefault(DATA_IMAGE, None)
		speaker_data.setdefault(DATA_NICKNAME, f"{speaker_data[DATA_ROOM]}")
		speaker_data.setdefault(DATA_FULL_NAME, f"{speaker_data[DATA_NICKNAME]} {'Display' if speaker_data[DATA_HAS_DISPLAY] else 'Speaker'}")
		speaker_data.setdefault(DATA_SHORT_NAME, "Display" if speaker_data[DATA_HAS_DISPLAY] else "Speaker")
		speaker_data.setdefault(DATA_ZONE, ZONE_BAKA_S_HOUSE)

		speaker_data[DATA_CHROMECAST].setdefault(DATA_ICON, ICON_MDI_CAST_AUDIO)
		speaker_data[DATA_CHROMECAST].setdefault(DATA_IS_INTEGRATED, True)
		speaker_data[DATA_CHROMECAST].setdefault(DATA_NICKNAME, speaker_data[DATA_NICKNAME])
		speaker_data[DATA_CHROMECAST].setdefault(DATA_FULL_NAME, speaker_data[DATA_FULL_NAME] if speaker_data[DATA_CHROMECAST][DATA_IS_INTEGRATED] else f"{speaker_data[DATA_FULL_NAME]} Chromecast")

	return speakers


async def get_speaker_groups(**kwds):
	speakers = await get_speakers(**kwds)

	speaker_groups = {
		"front_room_and_kitchen": {
			DATA_CHROMECAST: {
				DATA_SLUG: "front_room_and_kitchen",
			},
			DATA_GROUP_MEMBERS: ["front_room", "kitchen"],
		},
		"ground_floor": {
			DATA_CHROMECAST: {
				DATA_SLUG: "ground_floor_speakers",
			},
			DATA_GROUP_MEMBERS: ["basement", "bathroom", "front_room", "kitchen"],
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
	speaker_groups = await get_speaker_groups(**kwds)

	speaker_media_players = {
		f"{DOMAIN_MEDIA_PLAYER}.{speaker_data[DATA_CHROMECAST][DATA_SLUG]}": {
			ATTR_DEVICE_CLASS: DEVICE_CLASS_SPEAKER,
			ATTR_FRIENDLY_NAME: speaker_data[DATA_FULL_NAME],
			ATTR_ICON: speaker_data[DATA_ICON],
		} for speaker_data in speakers.values()
	}

	speaker_group_media_players = {
		f"{DOMAIN_MEDIA_PLAYER}.{speaker_group_data[DATA_CHROMECAST][DATA_SLUG]}": {
			ATTR_DEVICE_CLASS: DEVICE_CLASS_SPEAKER,
			ATTR_FRIENDLY_NAME: speaker_group_data[DATA_FULL_NAME],
			ATTR_ICON: speaker_group_data[DATA_ICON],
		} for speaker_group_data in speaker_groups.values()
	}

	speaker_unifi_device_trackers = {
		f"{DOMAIN_DEVICE_TRACKER}.{speaker_data[DATA_CHROMECAST][DATA_UNIFI_DEVICE_TRACKER_SLUG]}": {
			**({ATTR_ENTITY_PICTURE: speaker_data[DATA_IMAGE]} if speaker_data[DATA_IMAGE] is not None else {}),
			ATTR_FRIENDLY_NAME: f"{speaker_data[DATA_CHROMECAST][DATA_FULL_NAME]} Internet Connected",
			ATTR_ICON: speaker_data[DATA_CHROMECAST][DATA_ICON],
		} for speaker_data in speakers.values()
	}

	return {
		**speaker_media_players,
		**speaker_group_media_players,
		**speaker_unifi_device_trackers,
	}

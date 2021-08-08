"Added speakers to the frontend"

from custom_components.custom_backend.const import (
	CONF_BADGES,
	CONF_CARDS,
	CONF_CARD_MOD,
	CONF_CONTROLS,
	CONF_ENTITIES,
	CONF_ENTITY,
	CONF_GROUP,
	CONF_HIDE,
	CONF_ICON,
	CONF_INFO,
	CONF_LABEL,
	CONF_NAME,
	CONF_PANEL,
	CONF_PATH,
	CONF_POPUP_CARDS,
	CONF_POWER,
	CONF_PROGRESS,
	CONF_SHOW_HEADER_TOGGLE,
	CONF_SOURCE,
	CONF_STATE_COLOR,
	CONF_STYLE,
	CONF_TITLE,
	CONF_TYPE,
	DATA_CHROMECAST,
	DATA_ICON,
	DATA_NICKNAME,
	DOMAIN_MEDIA_PLAYER,
	ICON_MDI_SPEAKER_WIRELESS,
	TYPE_CUSTOM_MINI_MEDIA_PLAYER,
	TYPE_ENTITIES,
	TYPE_SECTION,
)

from custom_components.custom_backend.config.packages.speakers import get_speakers, get_speakers_groups

from .css import entities_with_label, speakers_mini_media_player_style
from .labels import get_label_lovelace_element

def make_speaker_mini_media_player_element(speaker_or_speaker_group_data):
	# TODO: replace / revamp with larger, Cupertino-esque version
	return {
		CONF_CARD_MOD: {
			CONF_STYLE: speakers_mini_media_player_style,
		},
		CONF_ENTITY: f"{DOMAIN_MEDIA_PLAYER}.{speaker_or_speaker_group_data[DATA_CHROMECAST]}",
		CONF_GROUP: True,
		CONF_HIDE: {
			CONF_CONTROLS: True,
			CONF_POWER: True,
			CONF_PROGRESS: True,
		},
		CONF_ICON: speaker_or_speaker_group_data[DATA_ICON],
		CONF_INFO: "scroll",
		CONF_NAME: speaker_or_speaker_group_data[DATA_NICKNAME],
		CONF_SOURCE: "icon",
		CONF_TYPE: TYPE_CUSTOM_MINI_MEDIA_PLAYER,
	}

async def get_speakers_view(**kwds):
	speakers = await get_speakers(**kwds)
	speaker_groups = await get_speakers_groups(**kwds)
	
	mini_media_player_entities = [
		await get_label_lovelace_element(nickname="Speakers", **kwds),
	]

	card_divider = {
		CONF_TYPE: TYPE_SECTION,
		CONF_LABEL: " ",
	}

	group_divider = {
		CONF_TYPE: TYPE_SECTION,
		CONF_LABEL: "Groups",
	}

	mini_media_player_entities.append(card_divider)
	for speaker_data in sorted(speakers.values(), key=lambda speaker_data: speaker_data[DATA_NICKNAME]):
		mini_media_player_entities.append(make_speaker_mini_media_player_element(speaker_data))
	
	mini_media_player_entities.append(group_divider)
	for speaker_group_data in sorted(speaker_groups.values(), key=lambda speaker_data: speaker_data[DATA_NICKNAME]):
		mini_media_player_entities.append(make_speaker_mini_media_player_element(speaker_group_data))
	

	speakers_mini_media_players = {
		CONF_CARD_MOD: {
			CONF_STYLE: entities_with_label,
		},
		CONF_ENTITIES: mini_media_player_entities,
		CONF_SHOW_HEADER_TOGGLE: False,
		CONF_STATE_COLOR: True,
		CONF_TYPE: TYPE_ENTITIES,
	}

	return {
		CONF_BADGES: [],
		CONF_CARDS: [speakers_mini_media_players],
		CONF_ICON: ICON_MDI_SPEAKER_WIRELESS,
		CONF_PANEL: True,
		CONF_PATH: "speakers",
		CONF_POPUP_CARDS: {},
		CONF_TITLE: "Speakers",
	}

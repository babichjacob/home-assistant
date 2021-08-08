"Added TVs to the frontend"

from custom_components.custom_backend.const import (
	CONF_BADGES,
	CONF_CARD,
	CONF_CARDS,
	CONF_CARD_MOD,
	CONF_ENTITIES,
	CONF_ENTITY,
	CONF_GROUP,
	CONF_HIDE,
	CONF_ICON,
	CONF_LABEL,
	CONF_NAME,
	CONF_PANEL,
	CONF_PATH,
	CONF_POPUP_CARDS,
	CONF_PROGRESS,
	CONF_REMOTE,
	CONF_SHOW_HEADER_TOGGLE,
	CONF_SOURCE,
	CONF_STATE_COLOR,
	CONF_STYLE,
	CONF_TITLE,
	CONF_TV,
	CONF_TYPE,
	CONF_VOLUME_STATELESS,
	DATA_COMES_FROM_ROKU,
	DATA_FULL_NAME,
	DATA_ICON,
	DATA_IS_TV,
	DATA_NICKNAME,
	DATA_ROKU,
	DOMAIN_MEDIA_PLAYER,
	DOMAIN_REMOTE,
	ICON_MDI_TELEVISION,
	TYPE_CUSTOM_MINI_MEDIA_PLAYER,
	TYPE_CUSTOM_ROKU_CARD,
	TYPE_ENTITIES,
	TYPE_SECTION,
)

from custom_components.custom_backend.config.packages.tvs import get_tvs

from .css import entities_with_label, mini_media_player_style
from .labels import get_label_lovelace_element

async def get_tvs_view(**kwds):
	tvs = await get_tvs(**kwds)
	
	mini_media_player_entities = [
		await get_label_lovelace_element(nickname="TVs", **kwds),
	]

	card_divider = {
		CONF_TYPE: TYPE_SECTION,
		CONF_LABEL: " ",
	}

	mini_media_player_entities.append(card_divider)

	for tv_data in sorted(tvs.values(), key=lambda tv_data: tv_data[DATA_NICKNAME]):
		# TODO: extract to make entity function and replace / revamp with larger Cupertino-esque bubbly version
		mini_media_player_entities.append({
			CONF_CARD_MOD: {
				CONF_STYLE: mini_media_player_style,
			},
			CONF_ENTITY: f"{DOMAIN_MEDIA_PLAYER}.{tv_data[DATA_ROKU][DATA_COMES_FROM_ROKU]}",
			CONF_GROUP: True,
			CONF_HIDE: {
				CONF_PROGRESS: True,
			},
			CONF_ICON: tv_data[DATA_ICON],
			CONF_NAME: tv_data[DATA_NICKNAME],
			CONF_SOURCE: "icon",
			CONF_TYPE: TYPE_CUSTOM_MINI_MEDIA_PLAYER,
			CONF_VOLUME_STATELESS: True,
		})
	

	tvs_mini_media_players = {
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
		CONF_CARDS: [tvs_mini_media_players],
		CONF_ICON: ICON_MDI_TELEVISION,
		CONF_PANEL: True,
		CONF_PATH: "tvs",
		CONF_POPUP_CARDS: {
			f"{DOMAIN_MEDIA_PLAYER}.{tv_data[DATA_ROKU][DATA_COMES_FROM_ROKU]}": {
				CONF_TITLE: f"{tv_data[DATA_FULL_NAME]} Remote",
				CONF_CARD: {
					CONF_ENTITY: f"{DOMAIN_MEDIA_PLAYER}.{tv_data[DATA_ROKU][DATA_COMES_FROM_ROKU]}",
					CONF_REMOTE: f"{DOMAIN_REMOTE}.{tv_data[DATA_ROKU][DATA_COMES_FROM_ROKU]}",
					CONF_TV: tv_data[DATA_ROKU][DATA_IS_TV],
					CONF_TYPE: TYPE_CUSTOM_ROKU_CARD,
				},
			} for tv_data in tvs.values()
		},
		CONF_TITLE: "TVs",
	}

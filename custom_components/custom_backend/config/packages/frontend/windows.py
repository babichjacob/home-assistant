"Added windows to the frontend"

from bisect import insort
from collections import defaultdict

from custom_components.custom_backend.const import (
	CONF_BADGES,
	CONF_CARDS,
	CONF_CARD_MOD,
	CONF_ENTITIES,
	CONF_ENTITY,
	CONF_ICON,
	CONF_LABEL,
	CONF_NAME,
	CONF_PANEL,
	CONF_PATH,
	CONF_POPUP_CARDS,
	CONF_SHOW_HEADER_TOGGLE,
	CONF_STATE_COLOR,
	CONF_STYLE,
	CONF_TITLE,
	CONF_TYPE,
	DATA_BLINDS,
	DATA_NICKNAME,
	DATA_ROOM_WITH_FREE_ACCESS,
	DATA_SHORT_NAME,
	DATA_WINDOW,
	DOMAIN_COVER,
	ICON_MDI_WINDOW_OPEN_VARIANT,
	TYPE_ENTITIES,
	TYPE_SECTION,
)

from custom_components.custom_backend.config.packages.windows import get_windows

from .labels import get_label_lovelace_element
from .theming import accent_color, entities_with_label

def make_window_element(window_slug, window_data):
	return {
		CONF_ENTITY: f"{DOMAIN_COVER}.{window_slug}_{DATA_WINDOW}",
		CONF_NAME: window_data[DATA_SHORT_NAME],
	}

def make_blinds_element(blinds_slug, blinds_data):
	return {
		CONF_ENTITY: f"{DOMAIN_COVER}.{blinds_slug}_{DATA_BLINDS}",
		CONF_NAME: blinds_data[DATA_SHORT_NAME],
	}

async def get_windows_view(**kwds):
	windows = await get_windows(**kwds)

	windows_per_room = defaultdict(list)
	for window_slug, window_data in windows.items():
		room = window_data[DATA_ROOM_WITH_FREE_ACCESS]
		insort(windows_per_room[room], (window_data[DATA_NICKNAME], window_slug, window_data))
	
	slider_entities = [
		await get_label_lovelace_element(nickname="Windows", **kwds),
	]
	
	for room in sorted(windows_per_room):
		section_divider_entity = {
			CONF_TYPE: TYPE_SECTION,
			CONF_LABEL: room,
		}
		slider_entities.append(section_divider_entity)

		for (window_short_name, window_slug, window_data) in windows_per_room[room]:
			slider_entities.append(make_blinds_element(window_slug, window_data[DATA_BLINDS]))
			slider_entities.append(make_window_element(window_slug, window_data))
	
	windows_card = {
		CONF_CARD_MOD: {
			CONF_STYLE: f"{entities_with_label}{accent_color('blue')}",
		},
		CONF_ENTITIES: slider_entities,
		CONF_SHOW_HEADER_TOGGLE: False,
		CONF_STATE_COLOR: True,
		CONF_TYPE: TYPE_ENTITIES,
	}

	return {
		CONF_BADGES: [],
		CONF_CARDS: [windows_card],
		CONF_ICON: ICON_MDI_WINDOW_OPEN_VARIANT,
		CONF_PANEL: True,
		CONF_PATH: "windows",
		CONF_TITLE: "windows",
	}

"Added garage doors to the frontend"

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
	DATA_FULL_NAME,
	DATA_NICKNAME,
	DOMAIN_COVER,
	ICON_MDI_GARAGE,
	TYPE_ENTITIES,
	TYPE_SECTION,
)

from custom_components.custom_backend.config.packages.garage_doors import get_garage_doors

from .theming import accent_color, entities_with_label
from .labels import get_label_lovelace_element

def make_lock_element(lock_slug, lock_data):
	return {
		CONF_ENTITY: f"{DOMAIN_COVER}.{lock_slug}",
		CONF_NAME: lock_data[DATA_FULL_NAME],
	}

async def get_garage_doors_view(**kwds):
	garage_doors = await get_garage_doors(**kwds)
	
	garage_doors_entity_rows = [
		await get_label_lovelace_element(nickname="Garage Door", **kwds),
	]

	card_divider = {
		CONF_TYPE: TYPE_SECTION,
		CONF_LABEL: " ",
	}

	garage_doors_entity_rows.append(card_divider)
	for lock_slug, lock_data in sorted(garage_doors.items(), key=lambda lock_slug_and_data: lock_slug_and_data[1][DATA_NICKNAME]):
		garage_doors_entity_rows.append(make_lock_element(lock_slug, lock_data))
	

	garage_doors_entities = {
		CONF_CARD_MOD: {
			CONF_STYLE: f"{entities_with_label}{accent_color('rose')}",
		},
		CONF_ENTITIES: garage_doors_entity_rows,
		CONF_SHOW_HEADER_TOGGLE: False,
		CONF_STATE_COLOR: True,
		CONF_TYPE: TYPE_ENTITIES,
	}

	return {
		CONF_BADGES: [],
		CONF_CARDS: [garage_doors_entities],
		CONF_ICON: ICON_MDI_GARAGE,
		CONF_PANEL: True,
		CONF_PATH: "garage-door",
		CONF_TITLE: "Garage Door",
	}

"Added locks to the frontend"

from custom_components.custom_backend.const import (
	CONF_ACTIVE,
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
	CONF_TOGGLE,
	CONF_TYPE,
	DATA_FULL_NAME,
	DATA_NICKNAME,
	DATA_PERSONALIZED,
	DATA_USER_ID,
	DOMAIN_LOCK,
	ICON_MDI_LOCK,
	STATE_UNLOCKED,
	TYPE_CUSTOM_TEMPLATE_ENTITY_ROW,
	TYPE_ENTITIES,
	TYPE_SECTION,
)

from custom_components.custom_backend.config.packages.locks import get_locks

from .css import entities_with_label
from .labels import get_label_lovelace_element

def make_lock_element(lock_slug, lock_data, people):
	people_username_to_person_slug = {
		person_data[DATA_FULL_NAME]: person_slug for person_slug, person_data in people.items() if person_data[DATA_USER_ID] is not None
	}

	return {
		CONF_ACTIVE: f"{{{{ is_state('{DOMAIN_LOCK}.{lock_slug}', {STATE_UNLOCKED!r}) }}}}",
		CONF_TYPE: TYPE_CUSTOM_TEMPLATE_ENTITY_ROW,
		CONF_ENTITY: f"{DOMAIN_LOCK}.{lock_slug}_{DATA_PERSONALIZED}_{{{{ ({people_username_to_person_slug})[user] }}}}",
		CONF_NAME: lock_data[DATA_NICKNAME],
		CONF_TOGGLE: True,
	}


async def get_locks_view(**kwds):
	people = kwds["people"]

	locks = await get_locks(**kwds)
	
	locks_entity_rows = [
		await get_label_lovelace_element(nickname="Locks", **kwds),
	]

	card_divider = {
		CONF_TYPE: TYPE_SECTION,
		CONF_LABEL: " ",
	}

	locks_entity_rows.append(card_divider)
	for lock_slug, lock_data in sorted(locks.items(), key=lambda lock_slug_and_data: lock_slug_and_data[1][DATA_NICKNAME]):
		locks_entity_rows.append(make_lock_element(lock_slug, lock_data, people))
	

	locks_entities = {
		CONF_CARD_MOD: {
			CONF_STYLE: entities_with_label,
		},
		CONF_ENTITIES: locks_entity_rows,
		CONF_SHOW_HEADER_TOGGLE: False,
		CONF_STATE_COLOR: True,
		CONF_TYPE: TYPE_ENTITIES,
	}

	return {
		CONF_BADGES: [],
		CONF_CARDS: [locks_entities],
		CONF_ICON: ICON_MDI_LOCK,
		CONF_PANEL: True,
		CONF_PATH: "locks",
		CONF_POPUP_CARDS: {},
		CONF_TITLE: "Locks",
	}

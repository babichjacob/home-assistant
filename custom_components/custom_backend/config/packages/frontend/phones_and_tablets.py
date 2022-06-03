"Added phones and tablets to the frontend"

from collections import Counter

from custom_components.custom_backend.const import (
	BROWSER_MOBILE_APP,
	CONF_ASPECT_RATIO,
	CONF_BADGES,
	CONF_CARDS,
	CONF_CARD_MOD,
	CONF_CARD_TYPE,
	CONF_DEFAULT_ZOOM,
	CONF_ENTITIES,
	CONF_HOURS_TO_SHOW,
	CONF_ICON,
	CONF_LABEL,
	CONF_LAYOUT_TYPE,
	CONF_PANEL,
	CONF_PATH,
	CONF_SHOW_HEADER_TOGGLE,
	CONF_STATE_COLOR,
	CONF_STYLE,
	CONF_TITLE,
	CONF_TYPE,
	DATA_BROWSERS,
	DATA_FULL_NAME,
	DATA_NICKNAME,
	DATA_OSES,
	DATA_SLUG,
	DATA_ZONES,
	DOMAIN_DEVICE_TRACKER,
	DOMAIN_ZONE,
	ICON_MDI_TABLET_CELLPHONE,
	TYPE_CUSTOM_HORIZONTAL_LAYOUT,
	TYPE_CUSTOM_HUI_ELEMENT,
	TYPE_CUSTOM_LAYOUT_CARD,
	TYPE_ENTITIES,
	TYPE_MAP,
	TYPE_SECTION,
)
from custom_components.custom_backend.utils import slugify

from custom_components.custom_backend.config.packages.phones import get_phones
from custom_components.custom_backend.config.packages.tablets import get_tablets

from .labels import get_label_lovelace_element, make_label_lovelace_element
from .theming import accent_color, entities_with_label


def make_phone_or_tablet_element(device_data, zones):
	zone_counts = Counter()

	zone_entities = set()
	for zone_data in zones.values():
		zone_slug = slugify(zone_data[DATA_FULL_NAME])
		zone_entities.add(f"{DOMAIN_ZONE}.{zone_slug}")
		zone_counts[zone_slug] += 1
	
	for zone_slug, zone_count in zone_counts.items():
		if zone_count == 1:
			continue
	
		for i in range(2, zone_count + 2):
			zone_entities.add(f"{DOMAIN_ZONE}.{zone_slug}_{i}")

	mobile_app_slug = None
	device_tracker_entities = []
	for os_data in device_data[DATA_OSES].values():
		mobile_app_data = os_data[DATA_BROWSERS].get(BROWSER_MOBILE_APP)
		if mobile_app_data is None:
			continue
		
		mobile_app_slug = mobile_app_data[DATA_SLUG]
		device_tracker_entities.append(f"{DOMAIN_DEVICE_TRACKER}.{mobile_app_slug}")

	return {
		CONF_CARD_MOD: {
			CONF_STYLE: entities_with_label,
		},
		CONF_CARD_TYPE: TYPE_ENTITIES,
		# TODO: fix
		CONF_ENTITIES: [] if mobile_app_slug is None else [
			make_label_lovelace_element(f"{DOMAIN_DEVICE_TRACKER}.{mobile_app_slug}", device_data[DATA_NICKNAME]),
			{
				CONF_ASPECT_RATIO: 1,
				CONF_CARD_TYPE: TYPE_MAP,
				CONF_DEFAULT_ZOOM: 13,
				CONF_HOURS_TO_SHOW: 16,
				CONF_ENTITIES: [*device_tracker_entities, *zone_entities],
				CONF_TYPE: TYPE_CUSTOM_HUI_ELEMENT,
			},
		],
		CONF_SHOW_HEADER_TOGGLE: False,
		CONF_TYPE: TYPE_CUSTOM_HUI_ELEMENT,
	}


async def get_phones_and_tablets_view(**kwds):
	zones = kwds[DATA_ZONES]

	phones = await get_phones(**kwds)
	tablets = await get_tablets(**kwds)
	
	phones_and_tablets_entities = [
		await get_label_lovelace_element(nickname="Phones & Tablets", **kwds),
	]

	card_divider = {
		CONF_TYPE: TYPE_SECTION,
		CONF_LABEL: " ",
	}

	phones_and_tablets_entities.append(card_divider)

	phones_and_tablets_cards = []
	for device_data in sorted([*phones.values(), *tablets.values()], key=lambda device_data: device_data[DATA_NICKNAME]):
		phones_and_tablets_cards.append(make_phone_or_tablet_element(device_data, zones))
	
	phones_and_tablets_entities.append({
		CONF_CARDS: phones_and_tablets_cards,
		# "card_type": "grid",
		# CONF_TYPE: TYPE_CUSTOM_HUI_ELEMENT,
		# "layout": "horizontal",
		# "layout": "vertical",
		# "column_width": "600px",
		# "justify_content": "stretch",
		CONF_CARD_MOD: {
			CONF_STYLE: """horizontal-layout { --column-max-width: 100% } #columns { margin: 0 !important }"""
		},
		"layout": {
			"width": 400,
		},
		CONF_LAYOUT_TYPE: TYPE_CUSTOM_HORIZONTAL_LAYOUT,
		CONF_TYPE: TYPE_CUSTOM_LAYOUT_CARD,
	})

	phones_and_tablets_entities_card = {
		CONF_CARD_MOD: {
			CONF_STYLE: f"{entities_with_label}{accent_color('amber')}",
		},
		CONF_ENTITIES: phones_and_tablets_entities,
		CONF_SHOW_HEADER_TOGGLE: False,
		CONF_STATE_COLOR: True,
		CONF_TYPE: TYPE_ENTITIES,
	}

	return {
		CONF_BADGES: [],
		CONF_CARDS: [phones_and_tablets_entities_card],
		CONF_ICON: ICON_MDI_TABLET_CELLPHONE,
		CONF_PANEL: True,
		CONF_PATH: "phones-and-tablets",
		CONF_TITLE: "Phones & Tablets",
	}

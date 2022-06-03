"Added lights to the frontend"

from bisect import insort
from collections import defaultdict
from itertools import dropwhile, zip_longest

from custom_components.custom_backend.const import (
	CONF_BADGES,
	CONF_CARDS,
	CONF_CARD_MOD,
	CONF_ENTITIES,
	CONF_ENTITY,
	CONF_HEAD,
	CONF_HIDE_STATE,
	CONF_ICON,
	CONF_ITEMS,
	CONF_LABEL,
	CONF_NAME,
	CONF_OPEN,
	CONF_PANEL,
	CONF_PATH,
	CONF_SHOW_HEADER_TOGGLE,
	CONF_STATE_COLOR,
	CONF_STYLE,
	CONF_TITLE,
	CONF_TOGGLE,
	CONF_TYPE,
	DATA_COMES_FROM_SWITCH,
	DATA_GROUP_MEMBERS,
	DATA_ICON,
	DATA_ROOM,
	DATA_SHORT_NAME,
	DOMAIN_LIGHT,
	ICON_MDI_LIGHTBULB_ON,
	TYPE_CUSTOM_FOLD_ENTITY_ROW,
	TYPE_CUSTOM_SLIDER_BUTTON_CARD,
	TYPE_CUSTOM_SLIDER_ENTITY_ROW,
	TYPE_ENTITIES,
	TYPE_SECTION,
)

from custom_components.custom_backend.config.packages.lights import get_light_groups, get_lights

from .labels import get_label_lovelace_element
from .theming import entities_with_label, accent_color


def make_light_element(light_slug, light_data, under_group_name):
	name = light_data[DATA_SHORT_NAME]
	if under_group_name is not None:
		prefix_removed = dropwhile(lambda group_word_and_name_word: group_word_and_name_word[0] == group_word_and_name_word[1], zip_longest(under_group_name.split(), name.split()))
		name = " ".join(group_word_and_name_word[1] for group_word_and_name_word in prefix_removed if group_word_and_name_word[1] is not None)

	# TODO: replace / revamp with swiper card
	return {
		CONF_ENTITY: f"{DOMAIN_LIGHT}.{light_slug}",
		CONF_HIDE_STATE: True,
		CONF_ICON: light_data[DATA_ICON],
		CONF_NAME: name,
		CONF_TOGGLE: bool(light_data[DATA_COMES_FROM_SWITCH]),
		CONF_TYPE: TYPE_CUSTOM_SLIDER_ENTITY_ROW,
	}
	return {
		CONF_CARD_MOD: {
			CONF_STYLE: """
				ha-card {
					--icon-color: rgba(255, 255, 255, 1.0);
					--label-color-on: rgba(255, 255, 255, 0.85);
					--label-color-off: rgba(255, 255, 255, 0.85);
					--state-color-on: rgba(255, 255, 255, 0.6);
					--state-color-off: rgba(255, 255, 255, 0.6);
					
					margin-bottom: 16px;
					margin-top: 16px;
					margin-right: 16px;

					height: 8rem;

					transition: unset;
				}

				@media (prefers-color-scheme: light) {
					ha-card {
						--card-background-color: #EEEEEE;
					}
				}

				@media (prefers-color-scheme: dark) {
					ha-card {
						--card-background-color: #333333;
					}
				}
			""",
		},
		# "compact": True,
		CONF_ENTITY: f"{DOMAIN_LIGHT}.{light_slug}",
		# CONF_HIDE_STATE: True,
		"action_button": {
			"mode": "custom",
			"show": True,
			"tap_action": {
				"action": "toggle",
			}
		},
		"icon": {
			"icon": light_data[DATA_ICON],
			"use_state_color": False,
		},
		"slider": {
			"background": "solid",
			"direction": "left-right",
			# "use_state_color": True,
			"use_state_color": False,
			# "use_percentage_bg_opacity": True,
			"use_percentage_bg_opacity": False,
		},
		CONF_NAME: name,
		# CONF_TOGGLE: bool(light_data[DATA_COMES_FROM_SWITCH]),
		CONF_TYPE: TYPE_CUSTOM_SLIDER_BUTTON_CARD,
	}


async def get_lights_view(**kwds):
	lights = await get_lights(**kwds)
	light_groups = await get_light_groups(**kwds)

	lights_per_room = defaultdict(list)
	for light_slug, light_data in lights.items():
		room = light_data[DATA_ROOM]
		lights_per_room[room].append(light_slug)

	lights_belonging_to_groups = set()
	for light_group_data in light_groups.values():
		lights_belonging_to_groups.update(light_group_data[DATA_GROUP_MEMBERS])
	
	slider_entities = [
		await get_label_lovelace_element(nickname="Lights", **kwds),
	]

	for room in sorted(lights_per_room):
		lights_in_room = lights_per_room[room]
		section_divider_entity = {
			CONF_TYPE: TYPE_SECTION,
			CONF_LABEL: room,
		}
		slider_entities.append(section_divider_entity)

		room_short_names_and_entities = []
		for light_slug in lights_in_room:
			if light_slug in lights_belonging_to_groups:
				continue
			light_data = lights[light_slug]
			light_entity = make_light_element(light_slug, light_data, None)
			insort(room_short_names_and_entities, (light_data[DATA_SHORT_NAME], light_entity))
		
		for light_group_slug, light_group_data in light_groups.items():
			if any(lights[light_slug][DATA_ROOM] != room for light_slug in light_group_data[DATA_GROUP_MEMBERS]):
				continue

			light_group_head_entity = {
				CONF_ENTITY: f"{DOMAIN_LIGHT}.{light_group_slug}",
				CONF_HIDE_STATE: True,
				CONF_NAME: "Whole Room" if light_group_data[DATA_SHORT_NAME] == room else light_group_data[DATA_SHORT_NAME],
				CONF_TYPE: TYPE_CUSTOM_SLIDER_ENTITY_ROW,
			}

			light_group_children_short_names_and_entities = sorted((lights[light_slug][DATA_SHORT_NAME], make_light_element(light_slug, lights[light_slug], light_group_data[DATA_SHORT_NAME])) for light_slug in light_group_data[DATA_GROUP_MEMBERS])

			light_group_entity = {
				CONF_HEAD: light_group_head_entity,
				CONF_ITEMS: [entity for (short_name, entity) in light_group_children_short_names_and_entities],
				CONF_OPEN: True,
				CONF_TYPE: TYPE_CUSTOM_FOLD_ENTITY_ROW,
			}
			insort(room_short_names_and_entities, (light_group_data[DATA_SHORT_NAME], light_group_entity))
		
		slider_entities.extend([entity for (short_name, entity) in room_short_names_and_entities])


	# TODO: WIP: TESTING
	custom_lights_element = {
		CONF_TYPE: "custom:custom-frontend-lights",
		"a key": "a value",
		"b key": "b value",
		"c key": {
			1: "one",
			2: "two",
		}
	}

	lights_sliders = {
		CONF_CARD_MOD: {
			CONF_STYLE: f"{entities_with_label}{accent_color('yellow')}",
		},
		CONF_ENTITIES: [*slider_entities, custom_lights_element],
		CONF_SHOW_HEADER_TOGGLE: False,
		CONF_STATE_COLOR: True,
		CONF_TYPE: TYPE_ENTITIES,
	}

	return {
		CONF_BADGES: [],
		CONF_CARDS: [lights_sliders],
		CONF_ICON: ICON_MDI_LIGHTBULB_ON,
		CONF_PANEL: True,
		CONF_PATH: "lights",
		CONF_TITLE: "Lights",
	}

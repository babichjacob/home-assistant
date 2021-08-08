"Keeping track of each person's room"

from custom_components.custom_backend.const import (
	CONF_ICON,
	CONF_NAME,
	CONF_OPTIONS,
	DATA_NICKNAME,
	DATA_ROOM,
	DOMAIN_INPUT_SELECT,
	ICON_MDI_FLOOR_PLAN,
	ROOMS_AT_BAKA_S_HOUSE,
	ZONE_BAKA_S_HOUSE,
)


async def generate_yaml(**kwds):
	people = kwds["people"]

	create_people_room_input_selects = {
		f"{person_slug}_{DATA_ROOM}": {
			CONF_ICON: ICON_MDI_FLOOR_PLAN,
			CONF_NAME: f"{person_data[DATA_NICKNAME]}'s Room at {ZONE_BAKA_S_HOUSE}",
			CONF_OPTIONS: ROOMS_AT_BAKA_S_HOUSE,
		} for person_slug, person_data in people.items()
	}

	return {
		DOMAIN_INPUT_SELECT: {
			**create_people_room_input_selects,
		}
	}

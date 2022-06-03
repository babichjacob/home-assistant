"Keeping track of each person's room"

from custom_components.custom_backend.const import (
	CONF_ICON,
	CONF_NAME,
	CONF_OPTIONS,
	DATA_NICKNAME,
	DATA_PEOPLE,
	DATA_ROOM,
	DATA_ROOMS,
	DATA_ZONE,
	DOMAIN_INPUT_SELECT,
	ICON_MDI_FLOOR_PLAN,
	ZONE_BAKA_S_HOUSE,
)


async def generate_yaml(**kwds):
	people = kwds[DATA_PEOPLE]
	rooms = kwds[DATA_ROOMS]

	rooms_at_baka_s_house = [room_name for room_name, room_data in rooms.items() if room_data[DATA_ZONE] == ZONE_BAKA_S_HOUSE]

	create_people_room_input_selects = {
		f"{person_slug}_{DATA_ROOM}": {
			CONF_ICON: ICON_MDI_FLOOR_PLAN,
			CONF_NAME: f"{person_data[DATA_NICKNAME]}'s Room at {ZONE_BAKA_S_HOUSE}",
			CONF_OPTIONS: rooms_at_baka_s_house,
		} for person_slug, person_data in people.items()
	}

	return {
		DOMAIN_INPUT_SELECT: {
			**create_people_room_input_selects,
		}
	}

"Registered our garage doors with the home automation and security system"

from custom_components.custom_backend.const import (
	ATTR_DEVICE_CLASS,
	ATTR_FRIENDLY_NAME,
	CONF_ENTITIES,
	CONF_INCLUDE,
	DATA_FULL_NAME,
	DATA_NICKNAME,
	DATA_ROOM_WITH_LIMITED_ACCESS,
	DATA_ROOM_WITH_FREE_ACCESS,
	DATA_ZONE,
	DEVICE_CLASS_GARAGE,
	DOMAIN_COVER,
	DOMAIN_RECORDER,
	ROOM_DRIVEWAY,
	ROOM_GARAGE,
	ZONE_BAKA_S_HOUSE,
)

async def get_garage_doors(**kwds):
	secrets = kwds["secrets"]

	garage_doors = {
		"garage_door": {
			DATA_ROOM_WITH_LIMITED_ACCESS: ROOM_DRIVEWAY,
			DATA_ROOM_WITH_FREE_ACCESS: ROOM_GARAGE,
		},
	}

	for garage_door_data in garage_doors.values():
		garage_door_data.setdefault(DATA_NICKNAME, garage_door_data[DATA_ROOM_WITH_FREE_ACCESS])
		garage_door_data.setdefault(DATA_FULL_NAME, f"{garage_door_data[DATA_NICKNAME]} Door")
		garage_door_data.setdefault(DATA_ZONE, ZONE_BAKA_S_HOUSE)

	return garage_doors


async def generate_yaml(**kwds):
	garage_doors = await get_garage_doors(**kwds)

	return {
		DOMAIN_RECORDER: {
			CONF_INCLUDE: {
				CONF_ENTITIES: [f"{DOMAIN_COVER}.{garage_door_slug}" for garage_door_slug in garage_doors],
			},
		},
	}


async def customize(**kwds):
	garage_doors = await get_garage_doors(**kwds)

	customize_covers = {
		f"{DOMAIN_COVER}.{garage_door_slug}": {
			ATTR_FRIENDLY_NAME: garage_door_data[DATA_FULL_NAME],
			ATTR_DEVICE_CLASS: DEVICE_CLASS_GARAGE,
		} for garage_door_slug, garage_door_data in garage_doors.items()
	}

	return {
		**customize_covers,
	}

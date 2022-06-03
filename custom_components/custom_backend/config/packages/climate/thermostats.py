"Registered all the thermostats with the home automation and security system"

from custom_components.custom_backend.const import (
	ATTR_FRIENDLY_NAME,
	ATTR_ICON,
	DATA_COMES_FROM_HOMEKIT,
	DATA_FULL_NAME,
	DATA_HUMIDITY_SENSOR,
	DATA_ICON,
	DATA_NICKNAME,
	DATA_ROOM,
	DATA_SHORT_NAME,
	DATA_SLUG,
	DATA_TEMPERATURE_SENSOR,
	DATA_ZONE,
	DOMAIN_CLIMATE,
	ICON_MDI_THERMOSTAT,
	ROOM_HALLWAY,
	ZONE_BAKA_S_HOUSE,
)

from custom_components.custom_backend.config.packages.lights import (get_customize_for_property_binary_sensors, get_customize_for_property_sensors, get_customize_for_indicator_lights, get_customize_for_switch_integrated_binary_sensors, get_customize_for_switch_integrated_sensors, integrated_sensors)


async def get_thermostats(**kwds):
	thermostats = {
		"hallway_thermostat": {
			DATA_COMES_FROM_HOMEKIT: {
				# TODO: fix these — wait what did I mean by that?
				DATA_HUMIDITY_SENSOR: "hallway_thermostat_current_humidity",
				DATA_SLUG: "hallway_thermostat_homekit",
				DATA_TEMPERATURE_SENSOR: "hallway_thermostat_current_temperature",
			},
			DATA_HUMIDITY_SENSOR: "hallway_thermostat_humidity",
			DATA_NICKNAME: "Thermostat",
			DATA_ROOM: ROOM_HALLWAY,
			DATA_TEMPERATURE_SENSOR: "hallway_thermostat_temperature",
			DATA_ZONE: ZONE_BAKA_S_HOUSE,
		},
	}

	for thermostat_data in thermostats.values():
		for sensor in integrated_sensors:
			thermostat_data.setdefault(sensor, None)

		thermostat_data.setdefault(DATA_FULL_NAME, thermostat_data[DATA_NICKNAME])
		thermostat_data.setdefault(DATA_SHORT_NAME, "Thermostat")

		thermostat_data.setdefault(DATA_ICON, ICON_MDI_THERMOSTAT)

	return thermostats


async def customize(**kwds):
	thermostats = await get_thermostats(**kwds)

	customize_thermostats = {
		f"{DOMAIN_CLIMATE}.{thermostat_slug}": {
			ATTR_FRIENDLY_NAME: f"{thermostat_data[DATA_FULL_NAME]}",
			ATTR_ICON: thermostat_data[DATA_ICON],
		} for thermostat_slug, thermostat_data in thermostats.items()
	}

	return {
		**get_customize_for_property_binary_sensors(thermostats),
		**get_customize_for_property_sensors(thermostats),
		**customize_thermostats,
	}


async def exposed_devices(**kwds):
	thermostats = await get_thermostats(**kwds)

	thermostat_entities = {
		f"{DOMAIN_CLIMATE}.{thermostat_slug}": {
			DATA_FULL_NAME: thermostat_data[DATA_FULL_NAME],
			DATA_ROOM: thermostat_data[DATA_ROOM],
			DATA_SHORT_NAME: thermostat_data[DATA_SHORT_NAME],
		} for thermostat_slug, thermostat_data in thermostats.items()
	}

	return {
		**thermostat_entities,
	}

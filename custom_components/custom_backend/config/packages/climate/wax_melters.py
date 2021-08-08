"Registered all the wax melters with the home automation and security system"

from custom_components.custom_backend.const import (
	ATTR_FRIENDLY_NAME,
	ATTR_ICON,
	DATA_BLUE,
	DATA_COMES_FROM_SWITCH,
	DATA_CURRENT_SENSOR,
	DATA_FULL_NAME,
	DATA_ICON,
	DATA_INDICATOR_LIGHTS,
	DATA_NICKNAME,
	DATA_POWER_SENSOR,
	DATA_RED,
	DATA_ROOM,
	DATA_SHORT_NAME,
	DATA_SLUG,
	DATA_VOLTAGE_SENSOR,
	DATA_ZONE,
	DOMAIN_SWITCH,
	ICON_MDI_CANDLE,
	ROOM_HALLWAY,
	ZONE_BAKA_S_HOUSE,
)


from custom_components.custom_backend.config.packages.lights import (get_customize_for_electricity_sensors, get_customize_for_indicator_lights)

async def get_wax_melters(**kwds):
	wax_melters = {
		"wax_melter": {
			DATA_COMES_FROM_SWITCH: {
				DATA_SLUG: "plug_awp04l_1_relay",
			},
			DATA_CURRENT_SENSOR: "plug_awp04l_1_current",
			DATA_NICKNAME: "Wax Melter",
			DATA_ICON: ICON_MDI_CANDLE,
			DATA_INDICATOR_LIGHTS: {
				DATA_RED: "plug_awp04l_1_led_red",
				DATA_BLUE: "plug_awp04l_1_led_blue",
			},
			DATA_POWER_SENSOR: "plug_awp04l_1_power",
			DATA_ROOM: ROOM_HALLWAY,
			DATA_VOLTAGE_SENSOR: "plug_awp04l_1_voltage",
			DATA_ZONE: ZONE_BAKA_S_HOUSE,
		},
	}

	for wax_melter_data in wax_melters.values():
		wax_melter_data.setdefault(DATA_COMES_FROM_SWITCH, {})
		wax_melter_data.setdefault(DATA_CURRENT_SENSOR, None)
		wax_melter_data.setdefault(DATA_POWER_SENSOR, None)
		wax_melter_data.setdefault(DATA_VOLTAGE_SENSOR, None)
		wax_melter_data.setdefault(DATA_ZONE, ZONE_BAKA_S_HOUSE)

		wax_melter_data.setdefault(DATA_FULL_NAME, wax_melter_data[DATA_NICKNAME])
		wax_melter_data.setdefault(DATA_SHORT_NAME, wax_melter_data[DATA_NICKNAME])

	return wax_melters


async def customize(**kwds):
	wax_melters = await get_wax_melters(**kwds)

	customize_wax_melters = {
		f"{DOMAIN_SWITCH}.{wax_melter_data[DATA_COMES_FROM_SWITCH][DATA_SLUG]}": {
			ATTR_FRIENDLY_NAME: f"{wax_melter_data[DATA_FULL_NAME]}",
			ATTR_ICON: wax_melter_data[DATA_ICON],
		} for wax_melter_data in wax_melters.values() if wax_melter_data[DATA_COMES_FROM_SWITCH]
	}

	return {
		**get_customize_for_electricity_sensors(wax_melters),
		**get_customize_for_indicator_lights(wax_melters),
		**customize_wax_melters,
	}

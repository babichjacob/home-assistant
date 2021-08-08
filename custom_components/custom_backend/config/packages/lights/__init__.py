"Registered all the lights with the home automation and security system"

from bisect import insort
from collections import defaultdict

from custom_components.custom_backend.const import (
	ATTR_DEVICE_CLASS,
	ATTR_FRIENDLY_NAME,
	ATTR_ICON,
	CONF_DISCOVERY,
	CONF_ENTITIES,
	CONF_ENTITY_ID,
	CONF_HOST,
	CONF_LIGHT,
	CONF_NAME,
	CONF_PLATFORM,
	CONF_SWITCH,
	DATA_ACTIONS,
	DATA_BLUE,
	DATA_COMES_FROM_SWITCH,
	DATA_CURRENT_SENSOR,
	DATA_FULL_NAME,
	DATA_GROUP_MEMBERS,
	DATA_HOST,
	DATA_ICON,
	DATA_INDICATOR_LIGHTS,
	DATA_NICKNAME,
	DATA_POWER_SENSOR,
	DATA_RED,
	DATA_ROOM,
	DATA_SHORT_NAME,
	DATA_SLUG,
	DATA_TPLINK_LIGHT,
	DATA_TPLINK_SWITCH,
	DATA_VOLTAGE_SENSOR,
	DATA_ZONE,
	DEVICE_CLASS_CURRENT,
	DEVICE_CLASS_POWER,
	DEVICE_CLASS_VOLTAGE,
	DOMAIN_LIGHT,
	DOMAIN_SENSOR,
	DOMAIN_SWITCH,
	DOMAIN_TPLINK,
	ICON_MDI_CAR_LIGHT_DIMMED,
	ICON_MDI_CEILING_LIGHT,
	ICON_MDI_CURRENT_AC,
	ICON_MDI_FIREPLACE,
	ICON_MDI_FLASH,
	ICON_MDI_FLOOR_LAMP,
	ICON_MDI_FOUNTAIN,
	ICON_MDI_LED_VARIANT_ON,
	ICON_MDI_LIGHTBULB_CFL,
	ICON_MDI_LIGHTBULB_GROUP,
	ICON_MDI_MIRROR,
	ICON_MDI_OUTDOOR_LAMP,
	ICON_MDI_SINE_WAVE,
	ICON_MDI_TELEVISION_AMBIENT_LIGHT,
	ICON_MDI_WALL_SCONCE_FLAT,
	LIGHT_PORCH,
	PLATFORM_GROUP,
	PLATFORM_SWITCH,
	ROOM_BATHROOM,
	ROOM_FRONT_ROOM,
	ROOM_FRONT_YARD,
	ROOM_HALLWAY,
	ROOM_JACOB_S_BEDROOM,
	ROOM_KITCHEN,
	ROOM_MATT_S_BEDROOM,
	ZONE_BAKA_S_HOUSE,
)
from custom_components.custom_backend.utils import slugify


async def get_lights(**kwds):
	lights = {
		"bathroom_salt_lamp": {
			DATA_COMES_FROM_SWITCH: {
				# TODO
				DATA_ACTIONS: {},
				DATA_SLUG: "plug_2_relay",
			},
			DATA_FULL_NAME: "Bathroom Salt Lamp",
			DATA_ICON: ICON_MDI_LIGHTBULB_CFL,
			DATA_INDICATOR_LIGHTS: {
				DATA_RED: "bathroom_salt_lamp",
				DATA_BLUE: "plug_2_blue_led",
			},
			DATA_ROOM: ROOM_BATHROOM,
			DATA_SHORT_NAME: "Salt Lamp",
			DATA_ZONE: ZONE_BAKA_S_HOUSE,
		},
		"fireplace_north": {
			DATA_ICON: ICON_MDI_FIREPLACE,
			DATA_SHORT_NAME: "Fireplace North",
			DATA_ROOM: ROOM_KITCHEN,
			DATA_ZONE: ZONE_BAKA_S_HOUSE,
		},
		"fireplace_south": {
			DATA_ICON: ICON_MDI_FIREPLACE,
			DATA_SHORT_NAME: "Fireplace South",
			DATA_ROOM: ROOM_KITCHEN,
			DATA_ZONE: ZONE_BAKA_S_HOUSE,
		},
		"front_room_behind_tv": {
			DATA_FULL_NAME: "Front Room Light Behind The TV",
			DATA_ICON: ICON_MDI_TELEVISION_AMBIENT_LIGHT,
			DATA_NICKNAME: "Front Room Light Behind The TV",
			DATA_ROOM: ROOM_FRONT_ROOM,
			DATA_SHORT_NAME: "Behind TV",
			DATA_ZONE: ZONE_BAKA_S_HOUSE,
		},
		"fountain": {
			DATA_COMES_FROM_SWITCH: {
				DATA_SLUG: "plug_3_relay",
			},
			DATA_FULL_NAME: "Fountain",
			DATA_ICON: ICON_MDI_FOUNTAIN,
			DATA_INDICATOR_LIGHTS: {
				DATA_RED: "fountain",
				DATA_BLUE: "plug_3_blue_led",
			},
			DATA_ROOM: ROOM_FRONT_YARD,
			DATA_ZONE: ZONE_BAKA_S_HOUSE,
		},
		"hallway_mirror": {
			DATA_ICON: ICON_MDI_MIRROR,
			DATA_SHORT_NAME: "Mirror",
			DATA_ROOM: ROOM_HALLWAY,
			DATA_ZONE: ZONE_BAKA_S_HOUSE,
		},
		"jacob_s_ceiling_east": {
			DATA_ICON: ICON_MDI_WALL_SCONCE_FLAT,
			DATA_SHORT_NAME: "Ceiling East",
			DATA_ROOM: ROOM_JACOB_S_BEDROOM,
			DATA_ZONE: ZONE_BAKA_S_HOUSE,
		},
		"jacob_s_ceiling_west": {
			DATA_ICON: ICON_MDI_WALL_SCONCE_FLAT,
			DATA_SHORT_NAME: "Ceiling West",
			DATA_ROOM: ROOM_JACOB_S_BEDROOM,
			DATA_ZONE: ZONE_BAKA_S_HOUSE,
		},
		"jacob_s_lamp_side": {
			DATA_ICON: ICON_MDI_CAR_LIGHT_DIMMED,
			DATA_SHORT_NAME: "Lamp Side",
			DATA_ROOM: ROOM_JACOB_S_BEDROOM,
			DATA_ZONE: ZONE_BAKA_S_HOUSE,
		},
		"jacob_s_lamp_top": {
			DATA_ICON: ICON_MDI_FLOOR_LAMP,
			DATA_SHORT_NAME: "Lamp Top",
			DATA_ROOM: ROOM_JACOB_S_BEDROOM,
			DATA_ZONE: ZONE_BAKA_S_HOUSE,
		},
		"kitchen_ceiling": {
			DATA_COMES_FROM_SWITCH: {
				DATA_SLUG: "kitchen_ceiling_light",
			},
			DATA_ICON: ICON_MDI_CEILING_LIGHT,
			DATA_SHORT_NAME: "Ceiling",
			DATA_ROOM: ROOM_KITCHEN,
			DATA_ZONE: ZONE_BAKA_S_HOUSE,
		},
		"matt_s_bedroom_1": {
			DATA_ICON: ICON_MDI_FLOOR_LAMP,
			DATA_SHORT_NAME: "1",
			DATA_ROOM: ROOM_MATT_S_BEDROOM,
			DATA_ZONE: ZONE_BAKA_S_HOUSE,
		},
		"matt_s_bedroom_2": {
			DATA_ICON: ICON_MDI_FLOOR_LAMP,
			DATA_SHORT_NAME: "2",
			DATA_ROOM: ROOM_MATT_S_BEDROOM,
			DATA_ZONE: ZONE_BAKA_S_HOUSE,
		},
		"matt_s_bedroom_behind_tv": {
			DATA_ICON: ICON_MDI_TELEVISION_AMBIENT_LIGHT,
			DATA_SHORT_NAME: "Behind TV",
			DATA_ROOM: ROOM_MATT_S_BEDROOM,
			DATA_ZONE: ZONE_BAKA_S_HOUSE,
		},
		LIGHT_PORCH: {
			DATA_ICON: ICON_MDI_OUTDOOR_LAMP,
			DATA_SHORT_NAME: "Porch",
			DATA_FULL_NAME: "Porch Light",
			DATA_ROOM: ROOM_FRONT_YARD,
			DATA_ZONE: ZONE_BAKA_S_HOUSE,
		},
		# "small_bulb_1": {
		# 	DATA_ICON: ICON_MDI_LAMP,
		# 	DATA_SHORT_NAME: "Dresser",
		# 	DATA_ROOM: ROOM_MATT_S_BEDROOM,
		# 	DATA_ZONE: ZONE_BAKA_S_HOUSE,
		# },
		# "small_bulb_2": {
		# 	DATA_ICON: ICON_MDI_WALL_SCONCE_ROUND_VARIANT,
		# 	DATA_SHORT_NAME: "Floor",
		# 	DATA_ROOM: ROOM_MATT_S_BEDROOM,
		# 	DATA_ZONE: ZONE_BAKA_S_HOUSE,
		# },
	}

	for light_data in lights.values():
		light_data.setdefault(DATA_COMES_FROM_SWITCH, {})
		light_data.setdefault(DATA_CURRENT_SENSOR, None)
		light_data.setdefault(DATA_POWER_SENSOR, None)
		light_data.setdefault(DATA_VOLTAGE_SENSOR, None)
		light_data.setdefault(DATA_ZONE, ZONE_BAKA_S_HOUSE)

		if DATA_FULL_NAME in light_data:
			light_data.setdefault(DATA_NICKNAME, light_data[DATA_FULL_NAME])
			light_data.setdefault(DATA_SHORT_NAME, light_data[DATA_FULL_NAME])
		elif DATA_NICKNAME in light_data:
			light_data.setdefault(DATA_FULL_NAME, f"{light_data[DATA_NICKNAME]} Light")
			light_data.setdefault(DATA_SHORT_NAME, light_data[DATA_NICKNAME])
		elif DATA_SHORT_NAME in light_data:
			light_data.setdefault(DATA_NICKNAME, f"{light_data[DATA_ROOM]} {light_data[DATA_SHORT_NAME]}")
			light_data.setdefault(DATA_FULL_NAME, f"{light_data[DATA_NICKNAME]} Light")

		light_data.setdefault(DATA_INDICATOR_LIGHTS, {})
		light_data[DATA_INDICATOR_LIGHTS].setdefault(DATA_BLUE, None)
		light_data[DATA_INDICATOR_LIGHTS].setdefault(DATA_RED, None)
	
	return lights


async def get_light_groups(**kwds):
	lights = await get_lights(**kwds)

	lights_per_room = defaultdict(list)
	for light_slug, light_data in lights.items():
		room = light_data[DATA_ROOM]
		lights_per_room[room].append(light_slug)
	
	room_groups = {}
	for room, lights_in_room in lights_per_room.items():
		rgb_lights_in_room = [light_slug for light_slug in lights_in_room if not lights[light_slug][DATA_COMES_FROM_SWITCH]]
		if len(rgb_lights_in_room) > 1:
			room_group_short_name = room
			room_group_nickname = room
			member_short_names = [lights[light_slug][DATA_SHORT_NAME].split() for light_slug in rgb_lights_in_room]

			first_word = member_short_names[0][0]
			if len({member_short_name[0] == first_word for member_short_name in member_short_names}) == 1:
				room_group_short_name = first_word
				room_group_nickname = first_word

			room_group_data = {
				DATA_GROUP_MEMBERS: rgb_lights_in_room,
				DATA_NICKNAME: room_group_nickname,
				DATA_SHORT_NAME: room_group_short_name,
			}

			room_group_slug = slugify(room_group_nickname)
			room_groups[room_group_slug] = room_group_data

	# TODO: enter custom groups here
	groups = {}

	groups.update(room_groups)

	for group_data in groups.values():
		group_data.setdefault(DATA_FULL_NAME, f"{group_data[DATA_NICKNAME]} Lights")
		if DATA_ICON not in group_data:
			icons = {lights[light_slug][DATA_ICON] for light_slug in group_data[DATA_GROUP_MEMBERS]}
			group_data[DATA_ICON] = icons.pop() if len(icons) == 1 else ICON_MDI_LIGHTBULB_GROUP

	return groups


async def generate_yaml(**kwds):
	secrets = kwds["secrets"]

	lights = await get_lights(**kwds)
	light_groups = await get_light_groups(**kwds)

	tplink_light_slugs = set()
	tplink_switch_slugs = set()

	for key in secrets:
		suffix = "_" + DATA_HOST
		if not key.endswith(suffix):
			continue

		prefix = DATA_TPLINK_LIGHT + "_"
		if key.startswith(prefix):
			tplink_light_slugs.add(key[len(prefix):-len(suffix)])
			continue
		
		prefix = DATA_TPLINK_SWITCH + "_"
		if key.startswith(prefix):
			tplink_switch_slugs.add(key[len(prefix):-len(suffix)])
			continue
	
	def error(string):
		raise Exception(string)

	create_light_switches = [
		{
			CONF_PLATFORM: PLATFORM_SWITCH,
			CONF_NAME: error(light_data[DATA_NICKNAME]) if slugify(light_data[DATA_NICKNAME]) != light_slug else light_data[DATA_NICKNAME],
			CONF_ENTITY_ID: f"{DOMAIN_SWITCH}.{light_data[DATA_COMES_FROM_SWITCH][DATA_SLUG]}",
		} for light_slug, light_data in lights.items() if light_data[DATA_COMES_FROM_SWITCH]
	]

	create_light_groups = [
		{
			CONF_PLATFORM: PLATFORM_GROUP,
			CONF_NAME: error(light_group_data[DATA_NICKNAME]) if slugify(light_group_data[DATA_NICKNAME]) != light_group_slug else light_group_data[DATA_NICKNAME],
			CONF_ENTITIES: [f"{DOMAIN_LIGHT}.{light_slug}" for light_slug in light_group_data[DATA_GROUP_MEMBERS]]
		} for light_group_slug, light_group_data in light_groups.items()
	]
	
	return {
		DOMAIN_LIGHT: [
			*create_light_switches,
			*create_light_groups,
		],

		DOMAIN_TPLINK: {
			CONF_DISCOVERY: True,
			CONF_LIGHT: [
				{
					CONF_HOST: secrets[f"{DATA_TPLINK_LIGHT}_{tplink_light_slug}_{DATA_HOST}"]
				} for tplink_light_slug in tplink_light_slugs
			],
			CONF_SWITCH: [
				{
					CONF_HOST: secrets[f"{DATA_TPLINK_SWITCH}_{tplink_switch_slug}_{DATA_HOST}"]
				} for tplink_switch_slug in tplink_switch_slugs
			]
		}
	}


def get_customize_for_indicator_lights(devices):
	colors = [
		(DATA_BLUE, "Blue"),
		(DATA_RED, "Red"),
	]

	return {
		f"{DOMAIN_LIGHT}.{device_data[DATA_INDICATOR_LIGHTS][color_channel]}": {
			ATTR_FRIENDLY_NAME: f"{device_data[DATA_FULL_NAME]} {color_name} Indicator Light",
			ATTR_ICON: ICON_MDI_LED_VARIANT_ON,
		} for (color_channel, color_name) in colors for device_slug, device_data in devices.items() if device_data[DATA_INDICATOR_LIGHTS][color_channel] is not None and device_data[DATA_INDICATOR_LIGHTS][color_channel] != device_slug
	}


def get_customize_for_electricity_sensors(devices):
	electricity_properties = [
		(DATA_CURRENT_SENSOR, "Current", DEVICE_CLASS_CURRENT, ICON_MDI_CURRENT_AC),
		(DATA_POWER_SENSOR, "Power", DEVICE_CLASS_POWER, ICON_MDI_FLASH),
		(DATA_VOLTAGE_SENSOR, "Voltage", DEVICE_CLASS_VOLTAGE, ICON_MDI_SINE_WAVE),
	]

	return {
		f"{DOMAIN_SENSOR}.{device_data[electricity_property]}": {
			ATTR_FRIENDLY_NAME: f"{device_data[DATA_FULL_NAME]} {electricity_name}",
			ATTR_DEVICE_CLASS: device_class,
			ATTR_ICON: icon,
		} for (electricity_property, electricity_name, device_class, icon) in electricity_properties for device_data in devices.values() if device_data[electricity_property] is not None
	}


async def customize(**kwds):
	lights = await get_lights(**kwds)
	light_groups = await get_light_groups(**kwds)

	customize_light_groups = {
		f"{DOMAIN_LIGHT}.{light_group_slug}": {
			ATTR_FRIENDLY_NAME: light_group_data[DATA_FULL_NAME],
			ATTR_ICON: light_group_data[DATA_ICON],
		} for light_group_slug, light_group_data in light_groups.items()
	}

	customize_lights = {
		f"{DOMAIN_LIGHT}.{light_slug}": {
			ATTR_FRIENDLY_NAME: light_data[DATA_FULL_NAME],
			ATTR_ICON: light_data[DATA_ICON],
		} for light_slug, light_data in lights.items()
	}

	customize_switches = {
		f"{DOMAIN_SWITCH}.{light_data[DATA_COMES_FROM_SWITCH][DATA_SLUG]}": {
			ATTR_FRIENDLY_NAME: f"{light_data[DATA_FULL_NAME]} Switch",
			ATTR_ICON: light_data[DATA_ICON],
		} for light_data in lights.values() if light_data[DATA_COMES_FROM_SWITCH]
	}

	return {
		**get_customize_for_indicator_lights(lights),
		**get_customize_for_electricity_sensors(lights),
		**customize_light_groups,
		**customize_lights,
		**customize_switches,
	}

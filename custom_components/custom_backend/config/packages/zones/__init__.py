"Registered every location with the home automation and security system"

from custom_components.custom_backend.const import (
	CONF_ICON,
	CONF_LATITUDE,
	CONF_LONGITUDE,
	CONF_NAME,
	CONF_RADIUS,
	DATA_FULL_NAME,
	DATA_ICON,
	DATA_LATITUDE,
	DATA_LONGITUDE,
	DATA_NAME,
	DATA_RADIUS,
	DATA_ZONE,
	DOMAIN_ZONE,
	ICON_MDI_CART,
	ICON_MDI_HAMBURGER,
	ICON_MDI_HOME_ACCOUNT,
	ICON_MDI_PIZZA,
	ICON_MDI_RICE,
	ICON_MDI_TACO,
)

def get_zones(**kwds):
	secrets = kwds["secrets"]


	def get_zone(slug):
		return {
			DATA_FULL_NAME: secrets[f"{DATA_ZONE}_{slug}_{DATA_NAME}"],
			DATA_ICON: secrets.get(f"{DATA_ZONE}_{slug}_{DATA_ICON}"),
			DATA_LATITUDE: secrets[f"{DATA_ZONE}_{slug}_{DATA_LATITUDE}"],
			DATA_LONGITUDE: secrets[f"{DATA_ZONE}_{slug}_{DATA_LONGITUDE}"],
			DATA_RADIUS: secrets[f"{DATA_ZONE}_{slug}_{DATA_RADIUS}"],
		}

	zone_slugs = set()
	for key in secrets:
		prefix = DATA_ZONE + "_"
		if not key.startswith(prefix):
			continue

		suffix = "_" + DATA_NAME
		if not key.endswith(suffix):
			continue

		zone_slugs.add(key[len(prefix):-len(suffix)])
	
	zones_without_customizations = {
		zone_slug: get_zone(zone_slug) for zone_slug in zone_slugs
	}

	customizations = {
		"asian_fusion_restaurant": {
			DATA_ICON: ICON_MDI_RICE,
		},
		"menards": {
			DATA_ICON: ICON_MDI_CART,
		},
		"mexican_restaurant": {
			DATA_ICON: ICON_MDI_TACO,
		},
		"pizzeria": {
			DATA_ICON: ICON_MDI_PIZZA,
		}
	}
	for house_slug in ["lisa_s_house", "london_s_old_house"]:
		customizations[house_slug] = {
			DATA_ICON: ICON_MDI_HOME_ACCOUNT,
		}
	for i in range(1, 3):
		customizations[f"little_caesars_{i}"] = {
			DATA_ICON: ICON_MDI_PIZZA,
		}
	for i in range(1, 3):
		customizations[f"mcdonald_s_{i}"] = {
			DATA_ICON: ICON_MDI_HAMBURGER,
		}
	for i in range(1, 2):
		customizations[f"meijer_{i}"] = {
			DATA_ICON: ICON_MDI_CART,
		}
	for i in range(1, 3):
		customizations[f"taco_bell_{i}"] = {
			DATA_ICON: ICON_MDI_TACO,
		}

	zones = {
		zone_slug: {
			**zones_without_customizations[zone_slug],
			**customizations.get(zone_slug, {})
		} for zone_slug in zones_without_customizations
	}

	return zones


async def generate_yaml(**kwds):
	zones = get_zones(**kwds)

	return {
		DOMAIN_ZONE: [
			{
				CONF_NAME: zone_data[DATA_FULL_NAME],
				CONF_LATITUDE: zone_data[DATA_LATITUDE],
				CONF_LONGITUDE: zone_data[DATA_LONGITUDE],
				CONF_RADIUS: zone_data[DATA_RADIUS],
				CONF_ICON: zone_data[DATA_ICON],
			} for zone_data in zones.values()
		],
	}

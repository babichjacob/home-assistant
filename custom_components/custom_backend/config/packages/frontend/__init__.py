"Set up the Home Assistant frontend"

from asyncio import gather

from custom_components.custom_backend.const import (
	CONF_DASHBOARDS,
	CONF_FILENAME,
	CONF_ICON,
	CONF_MODE,
	CONF_RESOURCES,
	CONF_TITLE,
	CONF_TYPE,
	CONF_URL,
	CONF_VIEWS,
	DOMAIN_BROWSER_MOD,
	DOMAIN_LOVELACE,
	ICON_MDI_DEVICES,
	ICON_MDI_VIEW_DASHBOARD
)

from .garage_doors import get_garage_doors_view
from .lights import get_lights_view
from .locks import get_locks_view
from .speakers import get_speakers_view
from .tvs import get_tvs_view
from .windows import get_windows_view


async def get_devices_by_type_dashboard(**kwds):
	return {
		CONF_VIEWS: await gather(
			get_garage_doors_view(**kwds),
			get_lights_view(**kwds),
			get_locks_view(**kwds),
			get_speakers_view(**kwds),
			get_tvs_view(**kwds),
			get_windows_view(**kwds),
		),
	}


async def get_rooms_dashboard(**kwds):
	# TODO
	...


async def generate_yaml(**kwds):
	return {
		DOMAIN_BROWSER_MOD: None,
		DOMAIN_LOVELACE: {
			CONF_MODE: "yaml",
			CONF_RESOURCES: [
				{
					CONF_TYPE: "module",
					CONF_URL: "/browser_mod.js",
				},
				{
					CONF_TYPE: "module",
					CONF_URL: "/hacsfiles/lovelace-card-mod/card-mod.js",
				},
				{
					CONF_TYPE: "module",
					CONF_URL: "/hacsfiles/lovelace-fold-entity-row/fold-entity-row.js",
				},
				{
					CONF_TYPE: "module",
					CONF_URL: "/hacsfiles/lovelace-slider-entity-row/slider-entity-row.js",
				},
				{
					CONF_TYPE: "module",
					CONF_URL: "/hacsfiles/lovelace-template-entity-row/template-entity-row.js",
				},
				{
					CONF_TYPE: "module",
					CONF_URL: "/hacsfiles/mini-media-player/mini-media-player-bundle.js",
				},
				{
					CONF_TYPE: "module",
					CONF_URL: "/hacsfiles/roku-card/roku-card.js",
				},
				{
					CONF_TYPE: "module",
					CONF_URL: "/hacsfiles/slider-button-card/slider-button-card.js",
				},
				{
					CONF_TYPE: "module",
					CONF_URL: "/local/custom-lovelace/mdx-icons/mdx-icons.js",
				},
			],
			CONF_DASHBOARDS: {
				"devices-by-type": {
					CONF_FILENAME: "ui-lovelace.yaml",
					CONF_ICON: ICON_MDI_DEVICES,
					CONF_MODE: "yaml",
					CONF_TITLE: "Devices",
				},
				"all-entities": {
					CONF_FILENAME: "_",
					CONF_ICON: ICON_MDI_VIEW_DASHBOARD,
					CONF_MODE: "yaml",
					CONF_TITLE: "All Entities",
				},
			}
		}
	}

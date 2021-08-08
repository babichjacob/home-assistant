"""The custom_backend component."""

from asyncio import gather
from importlib import import_module
from logging import getLogger
from pathlib import Path

from homeassistant import core

from .const import DOMAIN_CUSTOM_BACKEND
from .yaml import load, Loader


_LOGGER = getLogger(__name__)


current_directory = Path(__file__).parent


def get_data():
	with open("/config/secrets.yaml") as secrets_file:
		secrets = load(secrets_file, Loader=Loader)

	from .config.packages.people import get_people
	people = get_people(secrets=secrets)
	
	from .config.packages.zones import get_zones
	zones = get_zones(secrets=secrets)

	return {
		"people": people,
		"secrets": secrets,
		"zones": zones,
	}


def get_other_lifecycle_hooks():
	generatoring_pys = list(current_directory.glob("**/*.py"))

	lifecycle_hooks = {
		"async_setup": {},
		"async_setup_entry": {},
		"async_setup_platform_cover": {},
		"async_setup_platform_lock": {},
	}

	for generating_py in generatoring_pys:
		if generating_py.stem.startswith("_") and generating_py.stem != "__init__":
			continue

		if generating_py == current_directory / "__init__.py":
			continue
	
		import_location = generating_py.with_suffix(
			"").relative_to(current_directory)
		
		relative_import = f'.{str(import_location).replace("/", ".")}'

		imported_module = import_module(relative_import, package="custom_components.custom_backend")

		async_setup = getattr(imported_module, "async_setup", None)
		if async_setup is not None:
			lifecycle_hooks["async_setup"][relative_import] = async_setup

		async_setup_entry = getattr(imported_module, "async_setup_entry", None)
		if async_setup_entry is not None:
			lifecycle_hooks["async_setup_entry"][relative_import] = async_setup_entry

		async_setup_platform_cover = getattr(imported_module, "async_setup_platform_cover", None)
		if async_setup_platform_cover is not None:
			lifecycle_hooks["async_setup_platform_cover"][relative_import] = async_setup_platform_cover

		async_setup_platform_lock = getattr(imported_module, "async_setup_platform_lock", None)
		if async_setup_platform_lock is not None:
			lifecycle_hooks["async_setup_platform_lock"][relative_import] = async_setup_platform_lock

	return lifecycle_hooks


async def async_setup(hass: core.HomeAssistant, config: dict) -> bool:
	f"""Set up every subcomponent in custom_backend"""

	data = get_data()
	lifecycle_hooks = get_other_lifecycle_hooks()

	coroutines = [other_async_setup(hass, config, **data) for other_async_setup in lifecycle_hooks["async_setup"].values()]
	
	await gather(*coroutines)

	PLATFORMS = ["cover", "lock"]
	
	load_platforms_tasks = [hass.helpers.discovery.async_load_platform(platform, DOMAIN_CUSTOM_BACKEND, {}, config) for platform in PLATFORMS]
	await gather(*load_platforms_tasks)

	return True

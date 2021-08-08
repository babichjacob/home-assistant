from asyncio import gather

from homeassistant import core

from . import get_data, get_other_lifecycle_hooks


async def async_setup_platform(hass: core.HomeAssistant, config: dict, async_add_entities, discovery_info=None) -> bool:
	data = get_data()
	lifecycle_hooks = get_other_lifecycle_hooks()

	others = [value for key, value in lifecycle_hooks["async_setup_platform_lock"].items() if key != ".lock"]
	coroutines = [other_async_setup_platform(hass, config, async_add_entities, discovery_info, **data) for other_async_setup_platform in others]

	await gather(*coroutines)
	return True

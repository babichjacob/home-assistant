"Setting up automations for scanned tags (TODO WIP)"

from logging import getLogger

from homeassistant import core

from custom_components.custom_backend.const import (
	DATA_ACTION,
	DATA_TAG_ID,
	EVENT_TYPE_TAG_SCANNED,
)

from . import get_tags

_LOGGER = getLogger(__name__)


async def async_setup(hass: core.HomeAssistant, config: dict, **kwds) -> bool:
	tags = await get_tags(**kwds)

	async def tag_scanned(event):
		tag_id = event.data[DATA_TAG_ID]
		tag_data = tags[tag_id]

		action = tag_data[DATA_ACTION]

		await action(event=event, hass=hass, tag_data=tag_data)


	hass.bus.async_listen(EVENT_TYPE_TAG_SCANNED, tag_scanned)
	return True


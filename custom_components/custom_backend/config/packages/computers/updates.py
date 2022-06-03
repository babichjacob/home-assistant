"Configured computer updates"

from logging import getLogger

from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_state_change, async_track_time_change

from custom_components.custom_backend.const import (
	ATTR_FRIENDLY_NAME,
	ATTR_NEWEST_VERSION,
	CONF_ENTITY_ID,
	DATA_AUDIO,
	DATA_IMAGE,
	DATA_MESSAGE,
	DATA_PEOPLE,
	DATA_TEXT,
	DATA_TITLE,
	DATA_TTS,
	DOMAIN_BINARY_SENSOR,
	DOMAIN_HOMEASSISTANT,
	EVENT_TYPE_HOMEASSISTANT_START,
	IMAGE_HOME_ASSISTANT_LOGO,
	PERSON_JACOB,
	SERVICE_UPDATE_ENTITY,
	STATE_OFF,
)
from custom_components.custom_backend.utils import entity_state_to_readable_store, window

from custom_components.custom_backend.config.packages.notify import notify


_LOGGER = getLogger(__name__)

UPDATER_SLUG = "updater"


async def customize(**kwds):
	return {
		f"{DOMAIN_BINARY_SENSOR}.{UPDATER_SLUG}": {
			ATTR_FRIENDLY_NAME: "Home Assistant Updates Available",
		}
	}


async def async_setup(hass: HomeAssistant, config: dict, **kwds) -> bool:
	async def refresh_home_assistant_updates(point_in_time):
		await hass.services.async_call(DOMAIN_HOMEASSISTANT, SERVICE_UPDATE_ENTITY, {
			CONF_ENTITY_ID: f"{DOMAIN_BINARY_SENSOR}.{UPDATER_SLUG}",
		}, blocking=True)
	
	async def check_for_home_assistant_updates(from_state, to_state):
		if to_state is None:
			return
		if to_state.state == STATE_OFF:
			return
		
		if from_state.attributes.get(ATTR_NEWEST_VERSION) == to_state.attributes.get(ATTR_NEWEST_VERSION):
			return
		
		# TODO: any meaningful group or channel for this?
		await notify({
			DATA_AUDIO: {
				DATA_TTS: f"There's a new update available for Home Assistant! Version {to_state.attributes[ATTR_NEWEST_VERSION]} has just been released!",
			},
			DATA_IMAGE: IMAGE_HOME_ASSISTANT_LOGO,
			DATA_PEOPLE: [PERSON_JACOB],
			DATA_TEXT: {
				DATA_MESSAGE: f"Home Assistant can be updated to version {to_state.attributes[ATTR_NEWEST_VERSION]}",
				DATA_TITLE: "Update Available",
			}
		}, hass=hass, **kwds)

	async def setup_automations(event):
		async_track_time_change(hass, refresh_home_assistant_updates, hour=1, minute=00, second=00)
		async_track_time_change(hass, refresh_home_assistant_updates, hour=12+1, minute=00, second=00)

		[get_update_changes, subscribe_to_update_changes] = window(entity_state_to_readable_store(f"{DOMAIN_BINARY_SENSOR}.{UPDATER_SLUG}", hass=hass), 2)

		subscribe_to_update_changes(lambda: hass.async_create_task(check_for_home_assistant_updates(*get_update_changes())))

	hass.bus.async_listen(EVENT_TYPE_HOMEASSISTANT_START, setup_automations)	
	return True

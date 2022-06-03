"Registered all the windows with the home automation and security system"

from functools import partial
from logging import getLogger

from homeassistant import core
from homeassistant.helpers.event import async_track_state_change

from custom_components.custom_backend.const import (
	CONF_ENTITY_ID,
	CONF_ICON,
	CONF_NAME,
	CONF_OPTION,
	CONF_OPTIONS,
	DATA_BLINDS,
	DATA_FULL_NAME,
	DATA_ICON,
	DATA_LIGHT_LET_THROUGH,
	DATA_ROOM,
	DATA_SIRI,
	ICON_MDI_BLINDS,
	ICON_MDI_BLINDS_OPEN,
	ICON_MDI_WINDOW_CLOSED_VARIANT,
	ICON_MDI_WINDOW_OPEN_VARIANT,
	ROOM_KITCHEN,
	STATE_OPEN,
	STATE_OPEN,
	DATA_NICKNAME,
	DATA_ROOM_WITH_FREE_ACCESS,
	DATA_ROOM_WITH_LIMITED_ACCESS,
	DATA_SHORT_NAME,
	DATA_WINDOW,
	DEVICE_CLASS_BLINDS,
	DEVICE_CLASS_WINDOW,
	DOMAIN_COVER,
	DOMAIN_INPUT_SELECT,
	ROOM_BACKYARD,
	ROOM_BAKA_S_BEDROOM,
	ROOM_BATHROOM,
	ROOM_EAST_YARD,
	ROOM_FRONT_ROOM,
	ROOM_FRONT_YARD,
	ROOM_JACOB_S_BEDROOM,
	ROOM_JENNA_S_BEDROOM,
	ROOM_MATT_S_BEDROOM,
	SERVICE_SELECT_OPTION,
	STATE_CLOSED,
	STATE_CLOSING,
	STATE_OPEN,
	STATE_OPENING,
	STATE_UNKNOWN,
	WINDOW_JACOB_S_BEDROOM,
)
from custom_components.custom_backend.cover import CustomBackendCover
from custom_components.custom_backend.utils import derived_store, entity_state_to_readable_store


_LOGGER = getLogger(__name__)

async def get_windows(**kwds):
	# TODO: bay window in the kitchen and the sliding door there
	windows = {
		"baka_s_bedroom": {
			DATA_ROOM_WITH_FREE_ACCESS: ROOM_BAKA_S_BEDROOM,
			DATA_ROOM_WITH_LIMITED_ACCESS: ROOM_BACKYARD,
		},
		"bathroom": {
			DATA_ROOM_WITH_FREE_ACCESS: ROOM_BATHROOM,
			DATA_ROOM_WITH_LIMITED_ACCESS: ROOM_EAST_YARD,
		},
		"front_room": {
			DATA_ROOM_WITH_FREE_ACCESS: ROOM_FRONT_ROOM,
			DATA_ROOM_WITH_LIMITED_ACCESS: ROOM_FRONT_YARD,
		},
		WINDOW_JACOB_S_BEDROOM: {
			DATA_ROOM_WITH_FREE_ACCESS: ROOM_JACOB_S_BEDROOM,
			DATA_ROOM_WITH_LIMITED_ACCESS: ROOM_BACKYARD,
		},
		"jenna_s_bedroom": {
			DATA_ROOM_WITH_FREE_ACCESS: ROOM_JENNA_S_BEDROOM,
			DATA_ROOM_WITH_LIMITED_ACCESS: ROOM_FRONT_YARD,
		},
		"kitchen": {
			DATA_BLINDS: {
				DATA_SHORT_NAME: "Bay Window Blinds",
			},
			DATA_ROOM_WITH_FREE_ACCESS: ROOM_KITCHEN,
			DATA_ROOM_WITH_LIMITED_ACCESS: ROOM_BACKYARD,
			DATA_SHORT_NAME: "Bay Window",
		},
		"matt_s_bedroom": {
			DATA_ROOM_WITH_FREE_ACCESS: ROOM_MATT_S_BEDROOM,
			DATA_ROOM_WITH_LIMITED_ACCESS: ROOM_BACKYARD,
		},
	}

	def get_light_let_through_store(outside_brightness_store, *, hass, window_slug, window_data):
		blinds_state_store = entity_state_to_readable_store(f"{DOMAIN_COVER}.{window_slug}_{DATA_BLINDS}", hass=hass)

		# TODO: include outside angle
		def calculate_light_let_through(outside_brightness, blinds_state_object):
			# _LOGGER.error(f"DEBUG: outside_brightness is {outside_brightness}")

			if blinds_state_object.state == STATE_CLOSED:
				return (outside_brightness**0.875)/3
			
			return outside_brightness
			
		
		return derived_store([
			outside_brightness_store,
			blinds_state_store,
		], calculate_light_let_through)


	for window_slug, window_data in windows.items():
		window_data.setdefault(DATA_SHORT_NAME, "Window")
		window_data.setdefault(DATA_NICKNAME, window_data[DATA_ROOM_WITH_FREE_ACCESS])
		window_data.setdefault(DATA_FULL_NAME, f"{window_data[DATA_NICKNAME]} {window_data[DATA_SHORT_NAME]}")
		
		window_data.setdefault(DATA_ICON, {})
		window_data[DATA_ICON].setdefault(STATE_CLOSED, ICON_MDI_WINDOW_CLOSED_VARIANT)
		window_data[DATA_ICON].setdefault(STATE_OPEN, ICON_MDI_WINDOW_OPEN_VARIANT)

		# TODO
		window_data.setdefault(DATA_LIGHT_LET_THROUGH, partial(get_light_let_through_store, window_slug=window_slug, window_data=window_data))

		window_data.setdefault(DATA_BLINDS, {})
		window_data[DATA_BLINDS].setdefault(DATA_ROOM_WITH_FREE_ACCESS, window_data[DATA_ROOM_WITH_FREE_ACCESS])
		window_data[DATA_BLINDS].setdefault(DATA_SHORT_NAME, "Blinds")
		window_data[DATA_BLINDS].setdefault(DATA_NICKNAME, window_data[DATA_NICKNAME])
		window_data[DATA_BLINDS].setdefault(DATA_FULL_NAME, f"{window_data[DATA_BLINDS][DATA_NICKNAME]} {window_data[DATA_BLINDS][DATA_SHORT_NAME]}")

		window_data[DATA_BLINDS].setdefault(DATA_ICON, {})
		window_data[DATA_BLINDS][DATA_ICON].setdefault(STATE_CLOSED, ICON_MDI_BLINDS)
		window_data[DATA_BLINDS][DATA_ICON].setdefault(STATE_OPEN, ICON_MDI_BLINDS_OPEN)
	
	return windows


async def generate_yaml(**kwds):
	windows = await get_windows(**kwds)

	create_blinds_input_selects = {
		f"{window_slug}_{DATA_BLINDS}": {
			CONF_ICON: window_data[DATA_BLINDS][DATA_ICON][STATE_CLOSED],
			CONF_NAME: f"{window_data[DATA_BLINDS][DATA_FULL_NAME]} (State Storage)",
			CONF_OPTIONS: [
				STATE_UNKNOWN,
				STATE_CLOSED,
				STATE_CLOSING,
				STATE_OPEN,
				STATE_OPENING,
			],
		} for window_slug, window_data in windows.items()
	}

	create_window_input_selects = {
		f"{window_slug}_{DATA_WINDOW}": {
			CONF_ICON: window_data[DATA_ICON][STATE_OPEN],
			CONF_NAME: f"{window_data[DATA_FULL_NAME]} (State Storage)",
			CONF_OPTIONS: [
				STATE_UNKNOWN,
				STATE_CLOSED,
				STATE_CLOSING,
				STATE_OPEN,
				STATE_OPENING,
			],
		} for window_slug, window_data in windows.items()
	}

	return {
		DOMAIN_INPUT_SELECT: {
			**create_blinds_input_selects,
			**create_window_input_selects,
		},
	}





def get_window_state(*, stored_value):
	return stored_value


class Window(CustomBackendCover):
	def __init__(self, *, window_slug, window_data):
		super().__init__()

		self._window_slug = window_slug
		self._window_data = window_data

		self.entity_id = f"{DOMAIN_COVER}.{self.unique_id}"
	
	@property
	def unique_id(self):
		"""Return Unique ID string."""
		return f"{self._window_slug}_{DATA_WINDOW}"
	
	@property
	def device_class(self) -> str:
		return DEVICE_CLASS_WINDOW

	@property
	def icon(self):
		choice = STATE_OPEN

		if self.is_closed:
			choice = STATE_CLOSED

		return self._window_data[DATA_ICON][choice]

	@property
	def name(self):
		return self._window_data[DATA_FULL_NAME]

	async def async_open_cover(self, **kwds):
		"""Open the cover."""
		await self.hass.services.async_call(DOMAIN_INPUT_SELECT, SERVICE_SELECT_OPTION, {
			CONF_ENTITY_ID: f"{DOMAIN_INPUT_SELECT}.{self._window_slug}_{DATA_WINDOW}",
			CONF_OPTION: STATE_OPEN,
		}, blocking=True)
	
	async def async_close_cover(self, **kwds):
		"""Close cover."""
		await self.hass.services.async_call(DOMAIN_INPUT_SELECT, SERVICE_SELECT_OPTION, {
			CONF_ENTITY_ID: f"{DOMAIN_INPUT_SELECT}.{self._window_slug}_{DATA_WINDOW}",
			CONF_OPTION: STATE_CLOSED,
		}, blocking=True)

	async def async_update(self):
		input_select_state = self.hass.states.get(f"{DOMAIN_INPUT_SELECT}.{self._window_slug}_{DATA_WINDOW}")
		input_select_value = input_select_state.state
		new_state = get_window_state(stored_value=input_select_value)
		self._state = new_state

	async def async_added_to_hass(self):
		update_soon = lambda: self.async_schedule_update_ha_state(force_refresh=True)

		update_soon()
		async_track_state_change(hass=self.hass, entity_ids=[f"{DOMAIN_INPUT_SELECT}.{self._window_slug}_{DATA_WINDOW}"], action=lambda entity_id, from_state, to_state: update_soon())


def get_blinds_state(*, stored_value):
	return stored_value


class Blinds(CustomBackendCover):
	def __init__(self, *, blinds_slug, blinds_data):
		super().__init__()

		self._blinds_slug = blinds_slug
		self._blinds_data = blinds_data

		self.entity_id = f"{DOMAIN_COVER}.{self.unique_id}"
	
	@property
	def unique_id(self):
		"""Return Unique ID string."""
		return f"{self._blinds_slug}_{DATA_BLINDS}"
	
	@property
	def device_class(self) -> str:
		return DEVICE_CLASS_BLINDS

	@property
	def icon(self):
		choice = STATE_CLOSED

		if self.is_open:
			choice = STATE_OPEN

		return self._blinds_data[DATA_ICON][choice]

	@property
	def name(self):
		return self._blinds_data[DATA_FULL_NAME]

	async def async_open_cover(self, **kwds):
		"""Open the cover."""
		await self.hass.services.async_call(DOMAIN_INPUT_SELECT, SERVICE_SELECT_OPTION, {
			CONF_ENTITY_ID: f"{DOMAIN_INPUT_SELECT}.{self._blinds_slug}_{DATA_BLINDS}",
			CONF_OPTION: STATE_OPEN,
		}, blocking=True)
	
	async def async_close_cover(self, **kwds):
		"""Close cover."""
		await self.hass.services.async_call(DOMAIN_INPUT_SELECT, SERVICE_SELECT_OPTION, {
			CONF_ENTITY_ID: f"{DOMAIN_INPUT_SELECT}.{self._blinds_slug}_{DATA_BLINDS}",
			CONF_OPTION: STATE_CLOSED,
		}, blocking=True)

	async def async_update(self):
		input_select_state = self.hass.states.get(f"{DOMAIN_INPUT_SELECT}.{self._blinds_slug}_{DATA_BLINDS}")
		input_select_value = input_select_state.state
		new_state = get_blinds_state(stored_value=input_select_value)
		self._state = new_state

	async def async_added_to_hass(self):
		update_soon = lambda: self.async_schedule_update_ha_state(force_refresh=True)
		update_soon()

		async_track_state_change(hass=self.hass, entity_ids=[f"{DOMAIN_INPUT_SELECT}.{self._blinds_slug}_{DATA_BLINDS}"], action=lambda entity_id, from_state, to_state: update_soon())


async def async_setup_platform_cover(hass: core.HomeAssistant, config: dict, async_add_entities, discovery_info=None, **kwds) -> bool:
	windows = await get_windows(**kwds)
	
	window_entities = []
	blinds_entities = []

	for (window_slug, window_data) in windows.items():
		window_entity = Window(window_slug=window_slug, window_data=window_data)
		window_entities.append(window_entity)

		blinds_entity = Blinds(blinds_slug=window_slug, blinds_data=window_data[DATA_BLINDS])
		blinds_entities.append(blinds_entity)

	async_add_entities(window_entities)
	async_add_entities(blinds_entities)

	return True


async def exposed_devices(**kwds):
	windows = await get_windows(**kwds)

	blinds_entities = {
		f"{DOMAIN_COVER}.{window_slug}_{DATA_BLINDS}": {
			DATA_FULL_NAME: window_data[DATA_BLINDS][DATA_FULL_NAME],
			DATA_ROOM: window_data[DATA_BLINDS][DATA_ROOM_WITH_FREE_ACCESS],
			DATA_SHORT_NAME: window_data[DATA_BLINDS][DATA_SHORT_NAME],
			DATA_SIRI: False, # TODO: WIP
		} for window_slug, window_data in windows.items()
	}

	return {
		**blinds_entities,
	}

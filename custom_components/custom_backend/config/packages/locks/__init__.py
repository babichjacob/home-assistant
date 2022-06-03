"Registered our locks with the home automation and security system"

from asyncio import gather
from datetime import datetime
from logging import getLogger

from homeassistant import core
from homeassistant.components.lock import LockEntity
from homeassistant.helpers.event import async_track_state_change


from custom_components.custom_backend.const import (
	ATTR_DEVICE_CLASS,
	ATTR_FRIENDLY_NAME,
	ATTR_ICON,
	CHANNEL_LOCK_ACTIVITY,
	CONF_ENTITIES,
	CONF_ENTITY_ID,
	CONF_INCLUDE,
	DATA_ACCESS_CONTROL_LOCK_JAMMED,
	DATA_ACCESS_CONTROL_LOCK_STATE,
	DATA_ALARMLEVEL,
	DATA_ALARMTYPE,
	DATA_AUDIO,
	DATA_CAUSE,
	DATA_CHANNEL,
	DATA_COLOR,
	DATA_DATETIME,
	DATA_FULL_NAME,
	DATA_GOOGLE_ASSISTANT,
	DATA_GROUP,
	DATA_IMAGE,
	DATA_LOW_BATTERY_LEVEL,
	DATA_MESSAGE,
	DATA_NICKNAME,
	DATA_PEOPLE,
	DATA_PERSON,
	DATA_PERSONALIZED,
	DATA_PUSH,
	DATA_ROOM,
	DATA_ROOM_WITH_LIMITED_ACCESS,
	DATA_ROOM_WITH_FREE_ACCESS,
	DATA_SHORT_NAME,
	DATA_SIRI,
	DATA_TEXT,
	DATA_THE_CURRENT_STATUS_OF_THE_DOOR,
	DATA_TITLE,
	DATA_USER_ID,
	DATA_VIRTUAL_ASSISTANT,
	DATA_ZONE,
	DEVICE_CLASS_BATTERY,
	DEVICE_CLASS_PROBLEM,
	DOMAIN_BINARY_SENSOR,
	DOMAIN_CUSTOM_BACKEND,
	DOMAIN_LOCK,
	DOMAIN_RECORDER,
	DOMAIN_SENSOR,
	ICON_MDI_LOCK_ALERT,
	IMAGE_LOCK_UNLOCKED_COLOR,
	LOCK_DOOR_TO_THE_GARAGE,
	LOCK_FRONT_DOOR,
	NOTIFICATION_COLOR_GREEN,
	NOTIFICATION_COLOR_YELLOW,
	PUSH_SOUND_AUTOUNLOCK_HAPTIC,
	ROOM_FRONT_YARD,
	ROOM_GARAGE,
	ROOM_HALLWAY,
	ROOM_KITCHEN,
	SERVICE_LOCK,
	SERVICE_UNLOCK,
	SHARED_MEMORY_REMOTE_UNLOCKING,
	STATE_LOCKED,
	STATE_UNLOCKED,
	ZONE_BAKA_S_HOUSE,
)
from custom_components.custom_backend.utils import slugify
from custom_components.custom_backend.config.packages.notify import notify


_LOGGER = getLogger(__name__)


async def get_locks(**kwds):
	locks = {
		LOCK_DOOR_TO_THE_GARAGE: {
			DATA_NICKNAME: "Door to the Garage",
			DATA_ROOM_WITH_LIMITED_ACCESS: ROOM_GARAGE,
			DATA_ROOM_WITH_FREE_ACCESS: ROOM_KITCHEN,
		},
		LOCK_FRONT_DOOR: {
			DATA_NICKNAME: "Front Door",
			DATA_ROOM_WITH_LIMITED_ACCESS: ROOM_FRONT_YARD,
			DATA_ROOM_WITH_FREE_ACCESS: ROOM_HALLWAY,
		},
	}

	for lock_slug, lock_data in locks.items():
		lock_data.setdefault(DATA_ACCESS_CONTROL_LOCK_JAMMED, f"{lock_slug}_{DATA_ACCESS_CONTROL_LOCK_JAMMED}")
		lock_data.setdefault(DATA_ACCESS_CONTROL_LOCK_STATE, f"{lock_slug}_{DATA_ACCESS_CONTROL_LOCK_STATE}")
		lock_data.setdefault(DATA_ALARMLEVEL, f"{lock_slug}_{DATA_ALARMLEVEL}")
		lock_data.setdefault(DATA_ALARMTYPE, f"{lock_slug}_{DATA_ALARMTYPE}")
		lock_data.setdefault(DATA_FULL_NAME, f"{lock_data[DATA_NICKNAME]} Lock")
		lock_data.setdefault(DATA_LOW_BATTERY_LEVEL, f"{lock_slug}_{DATA_LOW_BATTERY_LEVEL}")
		lock_data.setdefault(DATA_SHORT_NAME, "Lock")
		lock_data.setdefault(DATA_THE_CURRENT_STATUS_OF_THE_DOOR, f"{lock_slug}_{DATA_THE_CURRENT_STATUS_OF_THE_DOOR}")
		lock_data.setdefault(DATA_ZONE, ZONE_BAKA_S_HOUSE)

	return locks


async def generate_yaml(**kwds):
	locks = await get_locks(**kwds)

	return {
		DOMAIN_RECORDER: {
			CONF_INCLUDE: {
				CONF_ENTITIES: [f"{DOMAIN_LOCK}.{lock_slug}" for lock_slug in locks],
			},
		},
	}


async def customize(**kwds):
	locks = await get_locks(**kwds)

	customize_door_statuses = {
		f"{DOMAIN_BINARY_SENSOR}.{lock_data[DATA_THE_CURRENT_STATUS_OF_THE_DOOR]}": {
			ATTR_FRIENDLY_NAME: f"{lock_data[DATA_NICKNAME]} Status (Inaccurate)",
		} for lock_data in locks.values()
	}

	customize_locks = {
		f"{DOMAIN_LOCK}.{lock_slug}": {
			ATTR_FRIENDLY_NAME: lock_data[DATA_FULL_NAME],
		} for lock_slug, lock_data in locks.items()
	}

	customize_lock_access_control_lock_jammeds = {
		f"{DOMAIN_BINARY_SENSOR}.{lock_data[DATA_ACCESS_CONTROL_LOCK_JAMMED]}": {
			ATTR_FRIENDLY_NAME: f"{lock_data[DATA_FULL_NAME]} Jammed (Inaccurate)",
			ATTR_DEVICE_CLASS: DEVICE_CLASS_PROBLEM,
		} for lock_data in locks.values()
	}

	customize_lock_access_control_states = {
		f"{DOMAIN_SENSOR}.{lock_data[DATA_ACCESS_CONTROL_LOCK_STATE]}": {
			ATTR_FRIENDLY_NAME: f"{lock_data[DATA_FULL_NAME]} State (Inaccurate)",
			ATTR_ICON: ICON_MDI_LOCK_ALERT,
		} for lock_data in locks.values()
	}

	customize_lock_alarm_levels = {
		f"{DOMAIN_SENSOR}.{lock_data[DATA_ALARMLEVEL]}": {
			ATTR_FRIENDLY_NAME: f"{lock_data[DATA_FULL_NAME]} Alarm Level",
			ATTR_ICON: ICON_MDI_LOCK_ALERT,
		} for lock_data in locks.values()
	}

	customize_lock_alarm_types = {
		f"{DOMAIN_SENSOR}.{lock_data[DATA_ALARMTYPE]}": {
			ATTR_FRIENDLY_NAME: f"{lock_data[DATA_FULL_NAME]} Alarm Type",
			ATTR_ICON: ICON_MDI_LOCK_ALERT,
		} for lock_data in locks.values()
	}

	customize_lock_low_battery_levels = {
		f"{DOMAIN_BINARY_SENSOR}.{lock_data[DATA_LOW_BATTERY_LEVEL]}": {
			ATTR_FRIENDLY_NAME: f"{lock_data[DATA_FULL_NAME]} Battery",
			ATTR_DEVICE_CLASS: DEVICE_CLASS_BATTERY,
		} for lock_data in locks.values()
	}


	return {
		**customize_door_statuses,
		**customize_locks,
		**customize_lock_access_control_lock_jammeds,
		**customize_lock_access_control_states,
		**customize_lock_alarm_levels,
		**customize_lock_alarm_types,
		**customize_lock_low_battery_levels,
	}

# TODO: move to packages/people/locks
class PersonalizedLock(LockEntity):
	should_poll = False

	def __init__(self, *, lock_slug, lock_data, person_slug, person_data, kwds):
		self._state = None

		self._lock_slug = lock_slug
		self._lock_data = lock_data
		self._person_slug = person_slug
		self._person_data = person_data
		self._kwds = kwds

		self.entity_id = f"{DOMAIN_LOCK}.{self.unique_id}"
	
	@property
	def unique_id(self):
		"""Return Unique ID string."""
		return f"{self._lock_slug}_{DATA_PERSONALIZED}_{self._person_slug}"
	
	@property
	def name(self):
		return f"{self._lock_data[DATA_FULL_NAME]} (personalized for {self._person_data[DATA_FULL_NAME]})"

	@property
	def available(self):
		"""Return if the device is online."""
		# TODO
		return True

	@property
	def is_locked(self):
		"""Return true if lock is locked, else False."""
		return self._state == STATE_LOCKED

	@property
	def is_unlocked(self):
		"""Return true if lock is unlocked, else False."""
		return self._state == STATE_UNLOCKED
	
	@property
	def state(self):
		if self.is_locked:
			return STATE_LOCKED
		if self.is_unlocked:
			return STATE_UNLOCKED
		
		return None

	async def async_lock(self):
		"""Lock all or specified locks. A code to lock the lock with may optionally be specified."""

		await self.hass.services.async_call(DOMAIN_LOCK, SERVICE_LOCK, {
			CONF_ENTITY_ID: f"{DOMAIN_LOCK}.{self._lock_slug}",
		}, blocking=True)

	async def async_unlock(self):
		"""Unlock all or specified locks. A code to unlock the lock with may optionally be specified."""
		
		self.hass.data[DOMAIN_CUSTOM_BACKEND][SHARED_MEMORY_REMOTE_UNLOCKING][self._lock_slug] = {
			DATA_DATETIME: datetime.now(),
			DATA_PERSON: self._person_slug,
		}
		
		notify_args = {
			DATA_AUDIO: {
				DATA_PUSH: PUSH_SOUND_AUTOUNLOCK_HAPTIC,
			},
			DATA_CAUSE: {
				DATA_PERSON: self._person_slug,
			},
			DATA_CHANNEL: CHANNEL_LOCK_ACTIVITY,
			DATA_COLOR: NOTIFICATION_COLOR_GREEN,
			DATA_IMAGE: IMAGE_LOCK_UNLOCKED_COLOR,
			DATA_TEXT: {
				DATA_MESSAGE: f"{self._person_data[DATA_NICKNAME]} unlocked the {self._lock_data[DATA_NICKNAME].lower()} with Home Assistant!",
				DATA_TITLE: f"{self._lock_data[DATA_NICKNAME]} Unlocked",
			},
		}

		notify_task = notify(notify_args, hass=self.hass, **self._kwds)

		unlock_task = self.hass.services.async_call(DOMAIN_LOCK, SERVICE_UNLOCK, {
			CONF_ENTITY_ID: f"{DOMAIN_LOCK}.{self._lock_slug}",
		}, blocking=True)

		await gather(notify_task, unlock_task)

	async def async_update(self):
		real_lock_state_object = self.hass.states.get(f"{DOMAIN_LOCK}.{self._lock_slug}")
		if real_lock_state_object is None:
			self._state = None
		else:
			self._state = real_lock_state_object.state

	async def async_added_to_hass(self):
		# TODO: replace with entity state stores, perhaps derived
		update_soon = lambda: self.async_schedule_update_ha_state(force_refresh=True)

		update_soon()
		async_track_state_change(hass=self.hass, entity_ids=[f"{DOMAIN_LOCK}.{self._lock_slug}"], action=lambda entity_id, from_state, to_state: update_soon())


class VirtualAssistantLock(LockEntity):
	should_poll = False

	def __init__(self, *, lock_slug, lock_data, virtual_assistant, kwds):
		self._state = None

		self._lock_slug = lock_slug
		self._lock_data = lock_data
		self._virtual_assistant = virtual_assistant
		self._kwds = kwds

		self.entity_id = f"{DOMAIN_LOCK}.{self.unique_id}"
	
	@property
	def unique_id(self):
		"""Return Unique ID string."""
		return f"{self._lock_slug}_{DATA_VIRTUAL_ASSISTANT}_{slugify(self._virtual_assistant)}"
	
	@property
	def name(self):
		return f"{self._lock_data[DATA_FULL_NAME]} (used through {self._virtual_assistant})"

	@property
	def available(self):
		"""Return if the device is online."""
		# TODO
		return True

	@property
	def is_locked(self):
		"""Return true if lock is locked, else False."""
		return self._state == STATE_LOCKED

	@property
	def is_unlocked(self):
		"""Return true if lock is unlocked, else False."""
		return self._state == STATE_UNLOCKED
	
	@property
	def state(self):
		if self.is_locked:
			return STATE_LOCKED
		if self.is_unlocked:
			return STATE_UNLOCKED
		
		return None

	async def async_lock(self):
		"""Lock all or specified locks. A code to lock the lock with may optionally be specified."""

		await self.hass.services.async_call(DOMAIN_LOCK, SERVICE_LOCK, {
			CONF_ENTITY_ID: f"{DOMAIN_LOCK}.{self._lock_slug}",
		}, blocking=True)

	async def async_unlock(self):
		"""Unlock all or specified locks. A code to unlock the lock with may optionally be specified."""
		
		self.hass.data[DOMAIN_CUSTOM_BACKEND][SHARED_MEMORY_REMOTE_UNLOCKING][self._lock_slug] = {
			DATA_DATETIME: datetime.now(),
			DATA_VIRTUAL_ASSISTANT: self._virtual_assistant,
		}
		
		notify_args = {
			DATA_AUDIO: {
				DATA_PUSH: PUSH_SOUND_AUTOUNLOCK_HAPTIC,
			},
			DATA_CHANNEL: CHANNEL_LOCK_ACTIVITY,
			DATA_COLOR: NOTIFICATION_COLOR_YELLOW,
			DATA_GROUP: "Household Activity",
			DATA_IMAGE: IMAGE_LOCK_UNLOCKED_COLOR,
			DATA_TEXT: {
				DATA_MESSAGE: f"The {self._lock_data[DATA_NICKNAME].lower()} was unlocked with {self._virtual_assistant}!",
				DATA_TITLE: f"{self._lock_data[DATA_NICKNAME]} Unlocked",
			},
		}

		notify_task = notify(notify_args, hass=self.hass, **self._kwds)

		unlock_task = self.hass.services.async_call(DOMAIN_LOCK, SERVICE_UNLOCK, {
			CONF_ENTITY_ID: f"{DOMAIN_LOCK}.{self._lock_slug}",
		}, blocking=True)

		await gather(notify_task, unlock_task)

	async def async_update(self):
		real_lock_state_object = self.hass.states.get(f"{DOMAIN_LOCK}.{self._lock_slug}")
		if real_lock_state_object is None:
			self._state = None
		else:
			self._state = real_lock_state_object.state

	async def async_added_to_hass(self):
		# TODO: replace with entity state stores, perhaps derived
		update_soon = lambda: self.async_schedule_update_ha_state(force_refresh=True)

		update_soon()
		async_track_state_change(hass=self.hass, entity_ids=[f"{DOMAIN_LOCK}.{self._lock_slug}"], action=lambda entity_id, from_state, to_state: update_soon())



async def async_setup(hass: core.HomeAssistant, config: dict, **kwds) -> bool:
	hass.data.setdefault(DOMAIN_CUSTOM_BACKEND, {})
	hass.data[DOMAIN_CUSTOM_BACKEND].setdefault(SHARED_MEMORY_REMOTE_UNLOCKING, {})


async def async_setup_platform_lock(hass: core.HomeAssistant, config: dict, async_add_entities, discovery_info=None, **kwds) -> bool:
	people = kwds[DATA_PEOPLE]
	locks = await get_locks(**kwds)
	
	lock_entities = []

	for lock_slug, lock_data in locks.items():
		for person_slug, person_data in people.items():
			if person_data[DATA_USER_ID] is None:
				continue
			
			personalized_lock_entity = PersonalizedLock(lock_slug=lock_slug, lock_data=lock_data, person_slug=person_slug, person_data=person_data, kwds=kwds)
			lock_entities.append(personalized_lock_entity)
		
		for virtual_assistant in {"Google Assistant", "Siri"}:
			virtual_assistant_lock_entity = VirtualAssistantLock(lock_slug=lock_slug, lock_data=lock_data, virtual_assistant=virtual_assistant, kwds=kwds)
			lock_entities.append(virtual_assistant_lock_entity)

	async_add_entities(lock_entities)
	return True


async def exposed_devices(**kwds):
	locks = await get_locks(**kwds)

	virtual_assistant_locks = {
		f"{DOMAIN_LOCK}.{lock_slug}_{DATA_VIRTUAL_ASSISTANT}_{slugify(virtual_assistant)}": {
			DATA_FULL_NAME: lock_data[DATA_FULL_NAME],
			DATA_GOOGLE_ASSISTANT: virtual_assistant == "Google Assistant",
			DATA_ROOM: lock_data[DATA_ROOM_WITH_LIMITED_ACCESS],
			DATA_SHORT_NAME: lock_data[DATA_SHORT_NAME],
			DATA_SIRI: virtual_assistant == "Siri",
		} for lock_slug, lock_data in locks.items() for virtual_assistant in ["Google Assistant", "Siri"]
	}

	return {
		**virtual_assistant_locks,
	}

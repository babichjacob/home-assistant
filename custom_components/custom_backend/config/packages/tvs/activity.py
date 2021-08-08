"Notify about the TVs"

from homeassistant import core
from homeassistant.helpers.condition import time
from homeassistant.helpers.event import async_track_time_change

from custom_components.custom_backend.const import DATA_DEVICES, DATA_MESSAGE, DATA_TEXT, DATA_TITLE, DEVICE_TYPE_SPEAKER
from custom_components.custom_backend.config.packages.notify import notify


# TODO: replace with calendar events

async def async_setup(hass: core.HomeAssistant, config: dict, **kwds) -> bool:
	"""Set up the Wheel of Fortune notification automation."""

	async def notify_for_wheel_of_fortune():
		await notify({
			DATA_DEVICES: [DEVICE_TYPE_SPEAKER],
			DATA_TEXT: {
				DATA_TITLE: "Wheel of Fortune",
				DATA_MESSAGE: "It's almost time for Wheel of Fortune! It'll be on in just a couple of minutes.",
			},
		}, hass=hass, **kwds)

	async def weekday_wheel_of_fortune_notification(*args, **kwds):
		"""At 6:57 pm on weekdays: inform people that Wheel of Fortune is coming on"""

		if time(weekday=["mon", "tue", "wed", "thu", "fri"], hass=hass):
			await notify_for_wheel_of_fortune()

	async_track_time_change(hass, weekday_wheel_of_fortune_notification, hour=12+6, minute=57, second=00)

	async def saturday_wheel_of_fortune_notification(*args, **kwds):
		"""At 7:27 pm on Saturdays: inform people that Wheel of Fortune is coming on"""

		if time(weekday=["sat"], hass=hass):
			await notify_for_wheel_of_fortune()

	async_track_time_change(hass, saturday_wheel_of_fortune_notification, hour=12+7, minute=27, second=00)

	return True

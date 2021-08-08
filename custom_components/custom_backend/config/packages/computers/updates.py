"Configured computer updates"

from custom_components.custom_backend.const import (
    ATTR_FRIENDLY_NAME,
)

# TODO: periodically refresh it and send notifications when updates are available

async def customize(**kwds):
    return {
        "binary_sensor.updater": {
            ATTR_FRIENDLY_NAME: "Home Assistant Updates Available",
        }
    }

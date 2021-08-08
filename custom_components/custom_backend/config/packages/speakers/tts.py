"Set up text-to-speech for speakers"

from datetime import timedelta

from custom_components.custom_backend.const import (
	CONF_PLATFORM,
	CONF_SERVICE_NAME,
	CONF_TIME_MEMORY,
	DOMAIN_TTS,
	PLATFORM_GOOGLE_TRANSLATE,
	SERVICE_GOOGLE_SAY,
)

async def generate_yaml(**kwds):
	return {
		DOMAIN_TTS: [
			{
				CONF_PLATFORM: PLATFORM_GOOGLE_TRANSLATE,
				CONF_SERVICE_NAME: SERVICE_GOOGLE_SAY,
				CONF_TIME_MEMORY: timedelta(hours=2).total_seconds(),
			}
		]
	}

# TODO: copy / modify chromecast_tts from old system

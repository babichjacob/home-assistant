"Added speakers to the frontend"

from custom_components.custom_backend.const import (
	CONF_BADGES,
	CONF_CARDS,
	CONF_CARD_MOD,
	CONF_CONTROLS,
	CONF_ENTITIES,
	CONF_ENTITY,
	CONF_GROUP,
	CONF_HIDE,
	CONF_ICON,
	CONF_INFO,
	CONF_LABEL,
	CONF_NAME,
	CONF_PANEL,
	CONF_PATH,
	CONF_POPUP_CARDS,
	CONF_POWER,
	CONF_PROGRESS,
	CONF_SHOW_HEADER_TOGGLE,
	CONF_SOURCE,
	CONF_STATE_COLOR,
	CONF_STYLE,
	CONF_TITLE,
	CONF_TYPE,
	DATA_CHROMECAST,
	DATA_ICON,
	DATA_NICKNAME,
	DATA_SLUG,
	DOMAIN_MEDIA_PLAYER,
	ICON_MDI_SPEAKER_WIRELESS,
	TYPE_CUSTOM_MINI_MEDIA_PLAYER,
	TYPE_ENTITIES,
	TYPE_SECTION,
)

from custom_components.custom_backend.config.packages.speakers import get_speakers, get_speaker_groups

from .labels import get_label_lovelace_element
from .theming import accent_color, entities_with_label, speakers_mini_media_player_style

def make_speaker_mini_media_player_element(speaker_or_speaker_group_data):
	# TODO: replace / revamp with larger, Cupertino-esque version
	# return {
	# 	CONF_CARD_MOD: {
	# 		CONF_STYLE: speakers_mini_media_player_style,
	# 	},
	# 	CONF_ENTITY: f"{DOMAIN_MEDIA_PLAYER}.{speaker_or_speaker_group_data[DATA_CHROMECAST][DATA_SLUG]}",
	# 	CONF_GROUP: True,
	# 	CONF_HIDE: {
	# 		CONF_CONTROLS: True,
	# 		CONF_POWER: True,
	# 		CONF_PROGRESS: True,
	# 	},
	# 	CONF_ICON: speaker_or_speaker_group_data[DATA_ICON],
	# 	CONF_INFO: "scroll",
	# 	CONF_NAME: speaker_or_speaker_group_data[DATA_NICKNAME],
	# 	CONF_SOURCE: "icon",
	# 	CONF_TYPE: TYPE_CUSTOM_MINI_MEDIA_PLAYER,
	# }
	return {
		CONF_CARD_MOD: {
			CONF_STYLE: """
				ha-card {
					margin-bottom: 16px;
					margin-top: 16px;
					margin-right: 16px;

					height: 8rem;

					transition: unset;
				}

				.--inactive .mmp-player {
					justify-content: center;
				}

				@media (prefers-color-scheme: light) {
					.--inactive .mmp-player {
						background-color: #EEEEEE;
					}
				}

				@media (prefers-color-scheme: dark) {
					.--inactive .mmp-player {
						background-color: #333333;
					}
				}

				/* todo */
				.mmp-progress__duration {
					opacity: 0.5;
				}

				.mmp-player {
					--mmp-name-font-weight: 600;
					height: 8rem;
					display: flex;
					flex-direction: column;
					justify-content: space-between;
				}
				/*.entity__info__name {
					font-size: 1.125rem;
				}*/

				/* mmp-progress {*/
				.mmp__container {
					--paper-progress-active-color: var(--primary-color) !important;
				}

				@media (prefers-color-scheme: light) {
					.mmp-player {
						background-color: rgba(238, 238, 238, 0.70);
					}
				}
				@media (prefers-color-scheme: dark) {
					.mmp-player {
						background-color: rgba(51, 51, 51, 0.70);
					}
				}

				@supports (backdrop-filter: blur(1px)) {
					@media (prefers-color-scheme: light) {
						.mmp-player {
							background-color: rgba(238, 238, 238, 0.50);
						}
					}
					@media (prefers-color-scheme: dark) {
						.mmp-player {
							background-color: rgba(51, 51, 51, 0.50);
						}
					}
					.mmp-player {
						backdrop-filter: blur(calc(0.75vw + 8px)) saturate(150%);
					}
				}

				@supports (-webkit-backdrop-filter: blur(1px)) {
					@media (prefers-color-scheme: light) {
						.mmp-player {
							background-color: rgba(238,238,238, 0.50);
						}
					}
					@media (prefers-color-scheme: dark) {
						.mmp-player {
							background-color: rgba(51, 51, 51, 0.50);
						}
					}
					.mmp-player {
						-webkit-backdrop-filter: blur(calc(0.75vw + 8px)) saturate(150%);
					}
				}
			""",
		},
		# TODO: material?!
		"artwork": "cover",
		CONF_ENTITY: f"{DOMAIN_MEDIA_PLAYER}.{speaker_or_speaker_group_data[DATA_CHROMECAST][DATA_SLUG]}",
		CONF_HIDE: {
			"runtime": False,
		},
		CONF_ICON: speaker_or_speaker_group_data[DATA_ICON],
		CONF_NAME: speaker_or_speaker_group_data[DATA_NICKNAME],
		CONF_TYPE: TYPE_CUSTOM_MINI_MEDIA_PLAYER,
		"volume_step": 5,
	}

async def get_speakers_view(**kwds):
	speakers = await get_speakers(**kwds)
	speaker_groups = await get_speaker_groups(**kwds)
	
	mini_media_player_entities = [
		await get_label_lovelace_element(nickname="Speakers", **kwds),
	]

	card_divider = {
		CONF_TYPE: TYPE_SECTION,
		CONF_LABEL: " ",
	}

	group_divider = {
		CONF_TYPE: TYPE_SECTION,
		CONF_LABEL: "Groups",
	}

	mini_media_player_entities.append(card_divider)
	for speaker_data in sorted(speakers.values(), key=lambda speaker_data: speaker_data[DATA_NICKNAME]):
		mini_media_player_entities.append(make_speaker_mini_media_player_element(speaker_data))
	
	mini_media_player_entities.append(group_divider)
	for speaker_group_data in sorted(speaker_groups.values(), key=lambda speaker_data: speaker_data[DATA_NICKNAME]):
		mini_media_player_entities.append(make_speaker_mini_media_player_element(speaker_group_data))
	

	speakers_mini_media_players = {
		CONF_CARD_MOD: {
			CONF_STYLE: f"{entities_with_label}{accent_color('lime')}",
		},
		CONF_ENTITIES: mini_media_player_entities,
		CONF_SHOW_HEADER_TOGGLE: False,
		CONF_STATE_COLOR: True,
		CONF_TYPE: TYPE_ENTITIES,
	}

	return {
		CONF_BADGES: [],
		CONF_CARDS: [speakers_mini_media_players],
		CONF_ICON: ICON_MDI_SPEAKER_WIRELESS,
		CONF_PANEL: True,
		CONF_PATH: "speakers",
		CONF_TITLE: "Speakers",
	}

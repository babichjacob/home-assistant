"Set up themes for the frontend"


from custom_components.custom_backend.const import CONF_DARK, CONF_LIGHT, CONF_MODES, CONF_THEMES, DATA_NESTED_THEME, DATA_TAILWIND, DOMAIN_FRONTEND, THEME_VALUE_ACCENT_COLOR, THEME_VALUE_APP_HEADER_BACKGROUND_COLOR, THEME_VALUE_APP_HEADER_TEXT_COLOR, THEME_VALUE_CARD_BACKGROUND_COLOR, THEME_VALUE_CODEMIRROR_ATOM, THEME_VALUE_CODEMIRROR_COMMENT, THEME_VALUE_CODEMIRROR_KEYWORD, THEME_VALUE_CODEMIRROR_NUMBER, THEME_VALUE_CODEMIRROR_PROPERTY, THEME_VALUE_CODEMIRROR_STRING, THEME_VALUE_ERROR_COLOR, THEME_VALUE_HA_CARD_BORDER_RADIUS, THEME_VALUE_LIGHT_PRIMARY_COLOR, THEME_VALUE_PAPER_ITEM_ICON_ACTIVE_COLOR, THEME_VALUE_PAPER_ITEM_ICON_COLOR, THEME_VALUE_PAPER_PROGRESS_ACTIVE_COLOR, THEME_VALUE_PAPER_SLIDER_KNOB_COLOR, THEME_VALUE_PAPER_SLIDER_PIN_START_COLOR, THEME_VALUE_PAPER_TOAST_BACKGROUND_COLOR, THEME_VALUE_PAPER_TOAST_COLOR, THEME_VALUE_PRIMARY_BACKGROUND_COLOR, THEME_VALUE_PRIMARY_COLOR, THEME_VALUE_PRIMARY_FONT_FAMILY, THEME_VALUE_SECONDARY_BACKGROUND_COLOR, THEME_VALUE_SECONDARY_TEXT_COLOR, THEME_VALUE_SECTION_HEADER_TEXT_COLOR, THEME_VALUE_SIDEBAR_SELECTED_ICON_COLOR, THEME_VALUE_SIDEBAR_SELECTED_TEXT_COLOR, THEME_VALUE_SLIDER_COLOR, THEME_VALUE_STATE_ICON_ACTIVE_COLOR, THEME_VALUE_STATE_ICON_COLOR, THEME_VALUE_DISABLED_TEXT_COLOR, THEME_VALUE_PRIMARY_TEXT_COLOR, THEME_VALUE_SUCCESS_COLOR, THEME_VALUE_SWITCH_CHECKED_BUTTON_COLOR, THEME_VALUE_SWITCH_CHECKED_TRACK_COLOR, THEME_VALUE_SWITCH_UNCHECKED_BUTTON_COLOR, THEME_VALUE_SWITCH_UNCHECKED_TRACK_COLOR, THEME_VALUE_WARNING_COLOR

from .colors import get_tailwind_2_color_palette, get_tailwind_2_gray_palette


FONTS_CUPERTINO = '-apple-system, BlinkMacSystemFont, Roboto, "Helvetica Neue", Arial, "Segoe UI", "Noto Sans", ui-sans-serif, system-ui, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji"'

def get_palette_info(palette_name):
	baseline = 500
	preferred_gray = "gray"

	if palette_name == "orange":
		baseline = 400
		preferred_gray = "warm-gray"
	elif palette_name == "amber":
		baseline = 400
		preferred_gray = "warm-gray"
	elif palette_name == "yellow":
		baseline = 400
		preferred_gray = "true-gray"
	elif palette_name == "lime":
		pass
	elif palette_name == "green":
		baseline = 600
	elif palette_name == "teal":
		preferred_gray = "cool-gray"
	elif palette_name == "cyan":
		preferred_gray = "cool-gray"
	elif palette_name == "sky":
		preferred_gray = "blue-gray"
	elif palette_name == "blue":
		preferred_gray = "blue-gray"
	elif palette_name == "indigo":
		preferred_gray = "cool-gray"
	elif palette_name == "purple":
		preferred_gray = "cool-gray"
	elif palette_name == "violet":
		preferred_gray = "cool-gray"
	elif palette_name == "rose":
		pass
	elif palette_name == "red":
		preferred_gray = "true-gray"

	return [baseline, preferred_gray]


async def get_themes(**kwds):
	tailwind_themes = {}

	tailwind_2_colors = get_tailwind_2_color_palette()
	tailwind_2_grays = get_tailwind_2_gray_palette()


	rounded = {
		"none": "0px",
		"sm": "2px",
		"DEFAULT": "4px",
		"md": "6px",
		"lg": "8px",
		"xl": "12px",
		"2xl": "16px",
		"3xl": "24px",
		"full": "9999px",
	}
	
	font_size = {
		"xs": "0.75rem",
		"sm": "0.875rem",
		"base": "1rem",
		"lg": "1.125rem",
		"xl": "1.25rem",
		"2xl": "1.5rem",
		"3xl": "1.875rem",
		"4xl": "2.25rem",
		"5xl": "3rem",
		"6xl": "3.75rem",
		"7xl": "4.5rem",
		"8xl": "6rem",
		"9xl": "8rem",
	}

	leading = {
		"none": "1",
		"tight": "1.25",
		"snug": "1.375",
		"normal": "1.5",
		"relaxed": "1.625",
		"loose": "2",
	}
	
	tracking = {
		"tighter": "-0.05em",
		"tight": "-0.025em",
		"normal": "0em",
		"wide": "0.025em",
		"wider": "0.05em",
		"widest": "0.1em",
	}

	main_accent_name = "sky"
	[main_baseline, _main_gray] = get_palette_info(main_accent_name)
	baseline = main_baseline

	preferred_gray = tailwind_2_grays["gray"]
	main_palette = tailwind_2_colors[main_accent_name]

	always_theme = {
		# Accent color, used for things like colored icons
		THEME_VALUE_ACCENT_COLOR: main_palette[baseline],
		THEME_VALUE_PRIMARY_COLOR: main_palette[baseline],
	}

	# Border radius
	always_theme.setdefault(THEME_VALUE_HA_CARD_BORDER_RADIUS, rounded["2xl"])
	...

	# Fonts
	always_theme.setdefault(THEME_VALUE_PRIMARY_FONT_FAMILY, FONTS_CUPERTINO)
	# tailwind_theme_data.setdefault("paper-font-body1_-_font-weight", "300")

	# Sidebar selected icon
	always_theme.setdefault(THEME_VALUE_SIDEBAR_SELECTED_ICON_COLOR, f"var(--{THEME_VALUE_SIDEBAR_SELECTED_TEXT_COLOR})")

	# todo: staging border color
	always_theme.setdefault("border-color", "transparent")
	always_theme.setdefault("divider-color", "transparent")
	always_theme.setdefault("entities-divider-color", "var(--divider-color)") # 2021.11?
	always_theme.setdefault("dialog-backdrop-filter", f"blur(12px)")
	always_theme.setdefault("ha-card-box-shadow", "none")
	# todo: staging page background color WIP INPROG 2021.11?
	always_theme.setdefault("ha-card-background", f"var(--{THEME_VALUE_CARD_BACKGROUND_COLOR})")
	always_theme.setdefault("lovelace-background", f"var(--{THEME_VALUE_CARD_BACKGROUND_COLOR})")
	# todo: fontSize map
	always_theme.setdefault("ha-card-header-font-size", "28px") # 2.5xl
	always_theme.setdefault("paper-font-common-base_-_font-family", f"var(--{THEME_VALUE_PRIMARY_FONT_FAMILY})")
	always_theme.setdefault("mdc-typography-font-family", f"var(--{THEME_VALUE_PRIMARY_FONT_FAMILY})")
	# mini media player
	always_theme.setdefault("mini-media-player-overlay-base-color", f"var(--{THEME_VALUE_PRIMARY_TEXT_COLOR})")
	# todo: staging card mod
	always_theme.setdefault("card-mod-theme", DATA_TAILWIND)
	always_theme.setdefault("card-mod-row", f"""
		.label {{
			font-size: {font_size["xl"]};
		}}
	""")
	
	always_theme.setdefault("card-mod-sidebar", f"""
		.iron-selected paper-icon-item {{
			z-index: 1;
		}}

		.iron-selected paper-icon-item::before {{
			opacity: 1 !important;
			background-color: var(--{THEME_VALUE_LIGHT_PRIMARY_COLOR});
			z-index: -1;
		}}
	""")
	
	always_theme.setdefault("card-mod-root-yaml", f"""
		:host {{
			filter: blur(8px);
		}}
	""")

	for palette_name, palette in tailwind_2_colors.items():
		[baseline, _gray] = get_palette_info(palette_name)

		# Accent color, used for things like colored icons
		always_theme[f"{DATA_NESTED_THEME}-{palette_name}-{THEME_VALUE_ACCENT_COLOR}"] = palette[baseline]
		always_theme[f"{DATA_NESTED_THEME}-{palette_name}-{THEME_VALUE_PRIMARY_COLOR}"] = palette[baseline]
		# Icon on
		always_theme[f"{DATA_NESTED_THEME}-{palette_name}-{THEME_VALUE_STATE_ICON_ACTIVE_COLOR}"] = f"var(--{DATA_NESTED_THEME}-{palette_name}-{THEME_VALUE_PRIMARY_COLOR})"
		always_theme[f"{DATA_NESTED_THEME}-{palette_name}-{THEME_VALUE_PAPER_ITEM_ICON_ACTIVE_COLOR}"] = f"var(--{DATA_NESTED_THEME}-{palette_name}-{THEME_VALUE_PRIMARY_COLOR})"
		# Icon off
		always_theme[f"{DATA_NESTED_THEME}-{palette_name}-{THEME_VALUE_STATE_ICON_COLOR}"] = f"var(--{THEME_VALUE_SECONDARY_TEXT_COLOR})"
		always_theme[f"{DATA_NESTED_THEME}-{palette_name}-{THEME_VALUE_PAPER_ITEM_ICON_COLOR}"] = f"var(--{THEME_VALUE_SECONDARY_TEXT_COLOR})"
		# Text colors
		# Section header
		always_theme[f"{DATA_NESTED_THEME}-{palette_name}-{THEME_VALUE_SECTION_HEADER_TEXT_COLOR}"] = f"var(--{DATA_NESTED_THEME}-{palette_name}-{THEME_VALUE_PRIMARY_COLOR})"

	# Icon on
	always_theme[THEME_VALUE_STATE_ICON_ACTIVE_COLOR] = always_theme[f"{DATA_NESTED_THEME}-{main_accent_name}-{THEME_VALUE_STATE_ICON_ACTIVE_COLOR}"]
	always_theme[THEME_VALUE_PAPER_ITEM_ICON_ACTIVE_COLOR] = always_theme[f"{DATA_NESTED_THEME}-{main_accent_name}-{THEME_VALUE_PAPER_ITEM_ICON_ACTIVE_COLOR}"]
	# Icon off
	always_theme[THEME_VALUE_STATE_ICON_COLOR] = always_theme[f"{DATA_NESTED_THEME}-{main_accent_name}-{THEME_VALUE_STATE_ICON_COLOR}"]
	always_theme[THEME_VALUE_PAPER_ITEM_ICON_COLOR] = always_theme[f"{DATA_NESTED_THEME}-{main_accent_name}-{THEME_VALUE_PAPER_ITEM_ICON_COLOR}"]

	light_theme = {
		# TODO: note to self
		# paper-toast-background-color: toast background
		# paper-toast-color: toast text
		# need to do switches because they still use an extratheme gray

		# Background colors
		THEME_VALUE_SECONDARY_BACKGROUND_COLOR: preferred_gray[100],
		# Card background color
		THEME_VALUE_CARD_BACKGROUND_COLOR: "white",
		# Header background + PWA manifest theme color
		THEME_VALUE_APP_HEADER_BACKGROUND_COLOR: "white",
		# Page background color
		THEME_VALUE_PRIMARY_BACKGROUND_COLOR: "white",
		# Sidebar selected background color
		THEME_VALUE_LIGHT_PRIMARY_COLOR: main_palette[100],
		# Toast background color
		# THEME_VALUE_PAPER_TOAST_BACKGROUND_COLOR: main_palette[baseline + 100],
		THEME_VALUE_PAPER_TOAST_BACKGROUND_COLOR: preferred_gray[800],
		
		# Extra colors
		THEME_VALUE_ERROR_COLOR: tailwind_2_colors["red"][600],
		THEME_VALUE_SUCCESS_COLOR: tailwind_2_colors["emerald"][600],
		THEME_VALUE_WARNING_COLOR: tailwind_2_colors["amber"][500],
		
		# Text colors
		THEME_VALUE_PRIMARY_TEXT_COLOR: preferred_gray[800],
		THEME_VALUE_SECONDARY_TEXT_COLOR: preferred_gray[600],
		THEME_VALUE_DISABLED_TEXT_COLOR: preferred_gray[400],
		# CodeMirror (e.x. YAML editor) colors
		# THEME_VALUE_CODEMIRROR_ATOM: tailwind_2_colors["orange"][500],
		# THEME_VALUE_CODEMIRROR_ATOM: tailwind_2_colors["red"][600],
		THEME_VALUE_CODEMIRROR_ATOM: tailwind_2_colors["blue"][600],
		THEME_VALUE_CODEMIRROR_COMMENT: preferred_gray[400],
		# THEME_VALUE_CODEMIRROR_KEYWORD: tailwind_2_colors["indigo"][500],
		# THEME_VALUE_CODEMIRROR_KEYWORD: tailwind_2_colors["amber"][600],
		# THEME_VALUE_CODEMIRROR_KEYWORD: tailwind_2_colors["cyan"][700],
		# THEME_VALUE_CODEMIRROR_KEYWORD: tailwind_2_colors["orange"][600],
		# THEME_VALUE_CODEMIRROR_KEYWORD: tailwind_2_colors["red"][600],
		THEME_VALUE_CODEMIRROR_KEYWORD: tailwind_2_colors["fuchsia"][500],
		# THEME_VALUE_CODEMIRROR_NUMBER: tailwind_2_colors["yellow"][500],
		# THEME_VALUE_CODEMIRROR_NUMBER: tailwind_2_colors["blue"][700],
		THEME_VALUE_CODEMIRROR_NUMBER: tailwind_2_colors["violet"][700],
		# THEME_VALUE_CODEMIRROR_PROPERTY: tailwind_2_colors["rose"][800],
		# THEME_VALUE_CODEMIRROR_PROPERTY: tailwind_2_colors["cyan"][700],
		THEME_VALUE_CODEMIRROR_PROPERTY: tailwind_2_colors["yellow"][600],
		# THEME_VALUE_CODEMIRROR_STRING: tailwind_2_colors["teal"][500],
		THEME_VALUE_CODEMIRROR_STRING: tailwind_2_colors["green"][600],
		# Header text color
		THEME_VALUE_APP_HEADER_TEXT_COLOR: preferred_gray[700],
		# Sidebar selected text color
		THEME_VALUE_SIDEBAR_SELECTED_TEXT_COLOR: main_palette[baseline],
		# Toast text color
		THEME_VALUE_PAPER_TOAST_COLOR: "white",
	}

	for palette_name, palette in tailwind_2_colors.items():
		[baseline, _gray] = get_palette_info(palette_name)

		# Switches
		# Switch on knob
		light_theme[f"{DATA_NESTED_THEME}-{palette_name}-{THEME_VALUE_SWITCH_CHECKED_BUTTON_COLOR}"] = "white"
		# Switch on track
		light_theme[f"{DATA_NESTED_THEME}-{palette_name}-{THEME_VALUE_SWITCH_CHECKED_TRACK_COLOR}"] = palette[baseline]
		# Switch off knob
		light_theme[f"{DATA_NESTED_THEME}-{palette_name}-{THEME_VALUE_SWITCH_UNCHECKED_BUTTON_COLOR}"] = "white"
		# Switch off track
		light_theme[f"{DATA_NESTED_THEME}-{palette_name}-{THEME_VALUE_SWITCH_UNCHECKED_TRACK_COLOR}"] = light_theme[THEME_VALUE_DISABLED_TEXT_COLOR]

		# Sliders
		# Slider knob
		light_theme[f"{DATA_NESTED_THEME}-{palette_name}-{THEME_VALUE_PAPER_SLIDER_KNOB_COLOR}"] = palette[baseline]
		light_theme[f"{DATA_NESTED_THEME}-{palette_name}-{THEME_VALUE_PAPER_SLIDER_PIN_START_COLOR}"] = light_theme[f"{DATA_NESTED_THEME}-{palette_name}-{THEME_VALUE_PAPER_SLIDER_KNOB_COLOR}"]
		# Slider track (colored part)
		light_theme[f"{DATA_NESTED_THEME}-{palette_name}-{THEME_VALUE_SLIDER_COLOR}"] = palette[baseline - 100]
		light_theme[f"{DATA_NESTED_THEME}-{palette_name}-{THEME_VALUE_PAPER_PROGRESS_ACTIVE_COLOR}"] = light_theme[f"{DATA_NESTED_THEME}-{palette_name}-{THEME_VALUE_SLIDER_COLOR}"]
		
	dark_theme = {
		# Background colors
		THEME_VALUE_SECONDARY_BACKGROUND_COLOR: preferred_gray[800],
		# Card background color
		THEME_VALUE_CARD_BACKGROUND_COLOR: preferred_gray[900],
		# Header background + PWA manifest theme color
		THEME_VALUE_APP_HEADER_BACKGROUND_COLOR: preferred_gray[900],
		# Page background color
		THEME_VALUE_PRIMARY_BACKGROUND_COLOR: preferred_gray[900],
		# Selected sidebar item backgrounud color
		THEME_VALUE_LIGHT_PRIMARY_COLOR: main_palette[baseline + 100],
		# Toast background color
		# THEME_VALUE_PAPER_TOAST_BACKGROUND_COLOR: main_palette[baseline + 100],
		THEME_VALUE_PAPER_TOAST_BACKGROUND_COLOR: "white",
		
		# Extra colors
		THEME_VALUE_ERROR_COLOR: tailwind_2_colors["red"][500],
		THEME_VALUE_SUCCESS_COLOR: tailwind_2_colors["emerald"][500],
		THEME_VALUE_WARNING_COLOR: tailwind_2_colors["amber"][500],
		
		# Text colors
		THEME_VALUE_PRIMARY_TEXT_COLOR: preferred_gray[200],
		THEME_VALUE_SECONDARY_TEXT_COLOR: preferred_gray[400],
		THEME_VALUE_DISABLED_TEXT_COLOR: preferred_gray[600],
		# CodeMirror (e.x. YAML editor) colors
		# THEME_VALUE_CODEMIRROR_ATOM: tailwind_2_colors["orange"][400], # TODO
		# THEME_VALUE_CODEMIRROR_COMMENT: preferred_gray[600], # TODO
		# THEME_VALUE_CODEMIRROR_KEYWORD: tailwind_2_colors["indigo"][400], # TODO
		# THEME_VALUE_CODEMIRROR_NUMBER: tailwind_2_colors["yellow"][400], # TODO
		# THEME_VALUE_CODEMIRROR_PROPERTY: tailwind_2_colors["rose"][300], #TODO
		# THEME_VALUE_CODEMIRROR_STRING: tailwind_2_colors["teal"][300], #TODO
		# Header text color
		THEME_VALUE_APP_HEADER_TEXT_COLOR: preferred_gray[200],
		# Sidebar selected text color
		THEME_VALUE_SIDEBAR_SELECTED_TEXT_COLOR: "white", # TODO: staging
		# Toast text color
		# THEME_VALUE_PAPER_TOAST_COLOR: "white",
		THEME_VALUE_PAPER_TOAST_COLOR: preferred_gray[800],
	}

	for palette_name, palette in tailwind_2_colors.items():
		[baseline, _gray] = get_palette_info(palette_name)

		# Switches
		# Switch on knob
		dark_theme[f"{DATA_NESTED_THEME}-{palette_name}-{THEME_VALUE_SWITCH_CHECKED_BUTTON_COLOR}"] = dark_theme[THEME_VALUE_PRIMARY_TEXT_COLOR]
		# Switch on track
		dark_theme[f"{DATA_NESTED_THEME}-{palette_name}-{THEME_VALUE_SWITCH_CHECKED_TRACK_COLOR}"] = palette[baseline]
		# Switch off knob
		dark_theme[f"{DATA_NESTED_THEME}-{palette_name}-{THEME_VALUE_SWITCH_UNCHECKED_BUTTON_COLOR}"] = dark_theme[THEME_VALUE_PRIMARY_TEXT_COLOR]
		# Switch off track
		dark_theme[f"{DATA_NESTED_THEME}-{palette_name}-{THEME_VALUE_SWITCH_UNCHECKED_TRACK_COLOR}"] = dark_theme[THEME_VALUE_DISABLED_TEXT_COLOR]

		# Sliders
		# Slider knob
		dark_theme[f"{DATA_NESTED_THEME}-{palette_name}-{THEME_VALUE_PAPER_SLIDER_KNOB_COLOR}"] = palette[baseline - 100]
		dark_theme[f"{DATA_NESTED_THEME}-{palette_name}-{THEME_VALUE_PAPER_SLIDER_PIN_START_COLOR}"] = dark_theme[f"{DATA_NESTED_THEME}-{palette_name}-{THEME_VALUE_PAPER_SLIDER_KNOB_COLOR}"]
		# Slider track (colored part)
		dark_theme[f"{DATA_NESTED_THEME}-{palette_name}-{THEME_VALUE_SLIDER_COLOR}"] = palette[baseline]
		dark_theme[f"{DATA_NESTED_THEME}-{palette_name}-{THEME_VALUE_PAPER_PROGRESS_ACTIVE_COLOR}"] = dark_theme[f"{DATA_NESTED_THEME}-{palette_name}-{THEME_VALUE_SLIDER_COLOR}"]
		
	tailwind_themes[DATA_TAILWIND] = {
		**always_theme,
		CONF_MODES: {
			CONF_LIGHT: light_theme,
			CONF_DARK: dark_theme,
		}
	}

	
	themes = {
		**tailwind_themes
	}

	return themes


# TODO
# section_labels_style = """
# 	hui-section-row { 
# 		font-size: 1.25rem; /* text-xl */
# 		/* font-weight: 700; /* font-bold */ */
# 	}
# 	.label {
# 		font-weight: 700; /* font-bold */
# 	}
# """
section_labels_style = ""

label_style = """
	.card-content > :first-child {
		font-size: var(--ha-card-header-font-size);
		font-weight: 700; /* font-bold */
		letter-spacing: -0.5px; /* tracking- between tight and tighter */
		line-height: 1.0; /* leading-none */
	}
"""

entities_with_label = f"""
{section_labels_style}
{label_style}
"""


# TODO: check if these aliases are unnecessary
mini_media_player_style = """
	.mmp-player {
		padding: 0 !important;
	}

	.--inactive .mmp-player {
		--mmp-icon-color: var(--paper-item-icon-color);
	}

	:not(.--inactive) .mmp-player {
		--mmp-icon-color: var(--paper-item-icon-active-color);
	}
"""

speakers_mini_media_player_style = f"""
{mini_media_player_style}

	mmp-powerstrip {{
		width: 56% !important;
		flex: initial !important;
		flex-shrink: 0 !important;
	}}
	.mmp-player {{
		padding: 0 !important;
	}}

	.mmp-player {{
		--mmp-icon-color: var(--paper-item-icon-color);
	}}
"""

def accent_color(accent_name):
	# [baseline, _preferred_gray] = get_palette_info(accent_name)

	# tailwind_2_colors = get_tailwind_2_color_palette()

	# palette = tailwind_2_colors[accent_name]

	return f"""
		ha-card {{
			--{THEME_VALUE_ACCENT_COLOR}: var(--{DATA_NESTED_THEME}-{accent_name}-{THEME_VALUE_ACCENT_COLOR});
			--{THEME_VALUE_PAPER_ITEM_ICON_ACTIVE_COLOR}: var(--{DATA_NESTED_THEME}-{accent_name}-{THEME_VALUE_PAPER_ITEM_ICON_ACTIVE_COLOR});
			--{THEME_VALUE_PAPER_ITEM_ICON_COLOR}: var(--{DATA_NESTED_THEME}-{accent_name}-{THEME_VALUE_PAPER_ITEM_ICON_COLOR});
			--{THEME_VALUE_PAPER_SLIDER_PIN_START_COLOR}: var(--{DATA_NESTED_THEME}-{accent_name}-{THEME_VALUE_PAPER_SLIDER_PIN_START_COLOR});
			--{THEME_VALUE_PAPER_PROGRESS_ACTIVE_COLOR}: var(--{DATA_NESTED_THEME}-{accent_name}-{THEME_VALUE_PAPER_PROGRESS_ACTIVE_COLOR});
			--{THEME_VALUE_PAPER_SLIDER_KNOB_COLOR}: var(--{DATA_NESTED_THEME}-{accent_name}-{THEME_VALUE_PAPER_SLIDER_KNOB_COLOR});
			--{THEME_VALUE_PRIMARY_COLOR}: var(--{DATA_NESTED_THEME}-{accent_name}-{THEME_VALUE_PRIMARY_COLOR});
			--{THEME_VALUE_SECTION_HEADER_TEXT_COLOR}: var(--{DATA_NESTED_THEME}-{accent_name}-{THEME_VALUE_SECTION_HEADER_TEXT_COLOR});
			--{THEME_VALUE_SLIDER_COLOR}: var(--{DATA_NESTED_THEME}-{accent_name}-{THEME_VALUE_SLIDER_COLOR});
			--{THEME_VALUE_STATE_ICON_ACTIVE_COLOR}: var(--{DATA_NESTED_THEME}-{accent_name}-{THEME_VALUE_STATE_ICON_ACTIVE_COLOR});
			--{THEME_VALUE_STATE_ICON_COLOR}: var(--{DATA_NESTED_THEME}-{accent_name}-{THEME_VALUE_STATE_ICON_COLOR});
			--{THEME_VALUE_SWITCH_CHECKED_BUTTON_COLOR}: var(--{DATA_NESTED_THEME}-{accent_name}-{THEME_VALUE_SWITCH_CHECKED_BUTTON_COLOR});
			--{THEME_VALUE_SWITCH_CHECKED_TRACK_COLOR}: var(--{DATA_NESTED_THEME}-{accent_name}-{THEME_VALUE_SWITCH_CHECKED_TRACK_COLOR});
			--{THEME_VALUE_SWITCH_UNCHECKED_BUTTON_COLOR}: var(--{DATA_NESTED_THEME}-{accent_name}-{THEME_VALUE_SWITCH_UNCHECKED_BUTTON_COLOR});
			--{THEME_VALUE_SWITCH_UNCHECKED_TRACK_COLOR}: var(--{DATA_NESTED_THEME}-{accent_name}-{THEME_VALUE_SWITCH_UNCHECKED_TRACK_COLOR});
		}}
	"""


async def generate_yaml(**kwds):
	themes = await get_themes(**kwds)

	return {
		DOMAIN_FRONTEND: {
			CONF_THEMES: {
				**themes
			}
		}
	}

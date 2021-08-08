"Set up themes for the frontend"


from custom_components.custom_backend.const import CONF_DARK, CONF_LIGHT, CONF_MODES, CONF_THEMES, DATA_TAILWIND, DOMAIN_FRONTEND, THEME_VALUE_ACCENT_COLOR, THEME_VALUE_APP_HEADER_BACKGROUND_COLOR, THEME_VALUE_APP_HEADER_TEXT_COLOR, THEME_VALUE_CARD_BACKGROUND_COLOR, THEME_VALUE_CODEMIRROR_ATOM, THEME_VALUE_CODEMIRROR_COMMENT, THEME_VALUE_CODEMIRROR_KEYWORD, THEME_VALUE_CODEMIRROR_NUMBER, THEME_VALUE_CODEMIRROR_PROPERTY, THEME_VALUE_CODEMIRROR_STRING, THEME_VALUE_ERROR_COLOR, THEME_VALUE_HA_CARD_BORDER_RADIUS, THEME_VALUE_PAPER_SLIDER_KNOB_COLOR, THEME_VALUE_PRIMARY_BACKGROUND_COLOR, THEME_VALUE_PRIMARY_COLOR, THEME_VALUE_PRIMARY_FONT_FAMILY, THEME_VALUE_SECONDARY_BACKGROUND_COLOR, THEME_VALUE_SECONDARY_TEXT_COLOR, THEME_VALUE_SECTION_HEADER_TEXT_COLOR, THEME_VALUE_SLIDER_COLOR, THEME_VALUE_STATE_ICON_ACTIVE_COLOR, THEME_VALUE_STATE_ICON_COLOR, THEME_VALUE_DISABLED_TEXT_COLOR, THEME_VALUE_PRIMARY_TEXT_COLOR, THEME_VALUE_SUCCESS_COLOR, THEME_VALUE_WARNING_COLOR

from .colors import get_tailwind_2_color_palette, get_tailwind_2_gray_palette


FONTS_CUPERTINO = '-apple-system, BlinkMacSystemFont, "San Francisco", system-ui, "Google Sans", "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji"'

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

	for palette_name, palette in tailwind_2_colors.items():
		preferred_gray = tailwind_2_grays["gray"]

		baseline = 500
		if palette_name == "orange":
			baseline = 400
			preferred_gray = tailwind_2_grays["warm-gray"]
		elif palette_name == "amber":
			baseline = 400
			preferred_gray = tailwind_2_grays["warm-gray"]
		elif palette_name == "yellow":
			baseline = 400
			preferred_gray = tailwind_2_grays["true-gray"]
		elif palette_name == "lime":
			baseline = 500
		elif palette_name == "green":
			baseline = 600
		elif palette_name == "teal":
			preferred_gray = tailwind_2_grays["cool-gray"]
		elif palette_name == "cyan":
			preferred_gray = tailwind_2_grays["cool-gray"]
		elif palette_name == "sky":
			preferred_gray = tailwind_2_grays["blue-gray"]
		elif palette_name == "blue":
			preferred_gray = tailwind_2_grays["blue-gray"]
		elif palette_name == "indigo":
			preferred_gray = tailwind_2_grays["cool-gray"]
		elif palette_name == "violet":
			preferred_gray = tailwind_2_grays["cool-gray"]
		elif palette_name == "rose":
			baseline = 400
		elif palette_name == "red":
			preferred_gray = tailwind_2_grays["true-gray"]


		# TODO: debugging
		# preferred_gray = tailwind_2_colors["violet"]

		always_theme = {
			# Accent color, used for things like colored icons
			THEME_VALUE_ACCENT_COLOR: palette[baseline],
			THEME_VALUE_PRIMARY_COLOR: palette[baseline],
		}

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
			
			# Extra colors
			THEME_VALUE_ERROR_COLOR: tailwind_2_colors["red"][600],
			THEME_VALUE_SUCCESS_COLOR: tailwind_2_colors["emerald"][600],
			THEME_VALUE_WARNING_COLOR: tailwind_2_colors["amber"][500],

			# Sliders
			THEME_VALUE_PAPER_SLIDER_KNOB_COLOR: palette[baseline],
			THEME_VALUE_SLIDER_COLOR: palette[baseline - 100],
			
			# Text colors
			THEME_VALUE_PRIMARY_TEXT_COLOR: preferred_gray[800],
			THEME_VALUE_SECONDARY_TEXT_COLOR: preferred_gray[600],
			THEME_VALUE_DISABLED_TEXT_COLOR: preferred_gray[400],
			# CodeMirror (e.x. YAML editor) colors
			THEME_VALUE_CODEMIRROR_ATOM: tailwind_2_colors["orange"][500],
			THEME_VALUE_CODEMIRROR_COMMENT: preferred_gray[400],
			THEME_VALUE_CODEMIRROR_KEYWORD: tailwind_2_colors["indigo"][500],
			THEME_VALUE_CODEMIRROR_NUMBER: tailwind_2_colors["yellow"][500],
			THEME_VALUE_CODEMIRROR_PROPERTY: tailwind_2_colors["rose"][800],
			THEME_VALUE_CODEMIRROR_STRING: tailwind_2_colors["teal"][500],
			# Header text color
			THEME_VALUE_APP_HEADER_TEXT_COLOR: preferred_gray[700],
		}

		dark_theme = {
			# Background colors
			THEME_VALUE_SECONDARY_BACKGROUND_COLOR: preferred_gray[800],
			# Card background color
			THEME_VALUE_CARD_BACKGROUND_COLOR: preferred_gray[900],
			# Header background + PWA manifest theme color
			THEME_VALUE_APP_HEADER_BACKGROUND_COLOR: preferred_gray[900],
			# Page background color
			THEME_VALUE_PRIMARY_BACKGROUND_COLOR: preferred_gray[900],
			
			# Extra colors
			THEME_VALUE_ERROR_COLOR: tailwind_2_colors["red"][500],
			THEME_VALUE_SUCCESS_COLOR: tailwind_2_colors["emerald"][500],
			THEME_VALUE_WARNING_COLOR: tailwind_2_colors["amber"][500],

			# Sliders
			THEME_VALUE_PAPER_SLIDER_KNOB_COLOR: palette[baseline - 100],
			THEME_VALUE_SLIDER_COLOR: palette[baseline],
			
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
		}

		tailwind_themes[f"{DATA_TAILWIND}-{palette_name}"] = {
			**always_theme,
			CONF_MODES: {
				CONF_LIGHT: light_theme,
				CONF_DARK: dark_theme,
			}
		}

	for tailwind_theme_data in tailwind_themes.values():
		# Border radius
		tailwind_theme_data.setdefault(THEME_VALUE_HA_CARD_BORDER_RADIUS, rounded["xl"])
		...

		# Fonts
		tailwind_theme_data.setdefault(THEME_VALUE_PRIMARY_FONT_FAMILY, FONTS_CUPERTINO)

		# Section header text
		tailwind_theme_data.setdefault(THEME_VALUE_SECTION_HEADER_TEXT_COLOR, f"var(--{THEME_VALUE_PRIMARY_COLOR})")

		# todo: staging border color
		tailwind_theme_data.setdefault("border-color", "transparent")
		tailwind_theme_data.setdefault("divider-color", "transparent")
		tailwind_theme_data.setdefault("dialog-backdrop-filter", f"blur({rounded['sm']})")
		tailwind_theme_data.setdefault("ha-card-box-shadow", "none")

	themes = {
		**tailwind_themes
	}

	for theme_data in themes.values():
		# Icon on
		theme_data.setdefault(THEME_VALUE_STATE_ICON_ACTIVE_COLOR, f"var(--{THEME_VALUE_PRIMARY_COLOR})")
		# Icon off
		theme_data.setdefault(THEME_VALUE_STATE_ICON_COLOR, f"var(--{THEME_VALUE_SECONDARY_TEXT_COLOR})")

	return themes


async def generate_yaml(**kwds):
	themes = await get_themes(**kwds)

	return {
		DOMAIN_FRONTEND: {
			CONF_THEMES: {
				**themes
			}
		}
	}

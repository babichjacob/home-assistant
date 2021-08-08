entities_with_label = """
	hui-section-row { 
		font-size: 1.25rem; 
	}
	
	.card-content > :first-child {
		font-size: 2em;
		font-weight: 700;
		letter-spacing: -0.5px;
		line-height: 1.0;
	}
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

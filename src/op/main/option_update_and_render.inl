void near option_update_and_render(void)
{
	static bool initialized = false;
	static bool input_allowed;

	if(!initialized) {
		// ZUN landmine: [COMMAND_LEFT] doesn't include the cursor. But then
		// again, it doesn't matter as the horizontal area unblitted by
		// option_unput_and_put() is larger in this menu anyway.
		menu_init(
			initialized,
			input_allowed,
			8,
			option_unput_and_put,
			COMMAND_LEFT,
			MENU_MAIN_W,
			main_choice_top(MC_COUNT)
		);
	}

	if(!key_det) {
		input_allowed = true;
	}
	if(!input_allowed) {
		return;
	}
	menu_update_vertical(key_det, OC_COUNT);

	if((key_det & INPUT_OK) || (key_det & INPUT_SHOT)) {
		switch(menu_sel) {
		case OC_RESET:
			resident->rank = RANK_NORMAL;
			resident->cfg_lives = CFG_LIVES_DEFAULT;
			resident->cfg_bombs = CFG_BOMBS_DEFAULT;
			resident->bgm_mode = SND_BGM_FM86;
			resident->se_mode = SND_SE_FM;
			resident->turbo_mode = true;
			snd_redetermine_modes_and_restart_bgm(true);
			initialized = false;
			break;
		case OC_QUIT:
			snd_se_play_force(11);
			return_from_option_to_main(initialized);
			break;
		default:
			goto right;
		}
	}

	// ZUN bloat: Could have been deduplicated.
	if(key_det & INPUT_RIGHT) {
	right:
		switch(menu_sel) {
		case OC_RANK:
			ring_inc_range(resident->rank, RANK_EASY, RANK_LUNATIC);
			break;
		case OC_LIVES:
			ring_inc_range(resident->cfg_lives, 1, CFG_LIVES_MAX);
			break;
		case OC_BOMBS:
			ring_inc_range(resident->cfg_bombs, 0, CFG_BOMBS_MAX);
			break;
		case OC_BGM:
			ring_inc_ge_range(resident->bgm_mode, SND_BGM_OFF, SND_BGM_FM86);
			snd_redetermine_modes_and_restart_bgm(false);
			break;
		case OC_SE:
			// ZUN bloat: Come on...
			if(resident->se_mode == SND_SE_OFF) {
				resident->se_mode = SND_SE_BEEP;
			} else {
				resident->se_mode--;
			}

			// ZUN bug: TH04 does not immediately apply SE mode changes.
			// (Same below for INPUT_LEFT.)
#if (GAME == 5)
			snd_redetermine_modes_and_reload_se();
#endif
			break;
		case OC_TURBO_OR_SLOW:
			resident->turbo_mode = (1 - resident->turbo_mode);
			break;
		}
		option_unput_and_put(menu_sel, COL_ACTIVE);
	}
	if(key_det & INPUT_LEFT) {
		switch(menu_sel) {
		case OC_RANK:
			ring_dec_range(resident->rank, RANK_EASY, RANK_LUNATIC);
			break;
		case OC_LIVES:
			ring_dec_range(resident->cfg_lives, 1, CFG_LIVES_MAX);
			break;
		case OC_BOMBS:
			ring_dec_range(resident->cfg_bombs, 0, CFG_BOMBS_MAX);
			break;
		case OC_BGM:
			// ZUN bloat: Come on...
			if(resident->bgm_mode == SND_BGM_OFF) {
				resident->bgm_mode = SND_BGM_FM86;
			} else {
				resident->bgm_mode--;
			}
			snd_redetermine_modes_and_restart_bgm(false);
			break;
		case OC_SE:
			ring_inc_ge_range(resident->se_mode, SND_SE_OFF, SND_SE_BEEP);
#if (GAME == 5)
			snd_redetermine_modes_and_reload_se();
#endif
			break;
		case OC_TURBO_OR_SLOW:
			resident->turbo_mode = (1 - resident->turbo_mode);
			break;
		}
		option_unput_and_put(menu_sel, COL_ACTIVE);
	}

	if(key_det & INPUT_CANCEL) {
		return_from_option_to_main(initialized);
	}
	if(key_det) {
		input_allowed = false;
	}
}

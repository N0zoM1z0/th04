void near main_update_and_render(void)
{
	static bool initialized = false;
	static bool input_allowed;

	if(!initialized) {
		main_menu_unused_1 = 0;

		// ZUN bloat: Way too wide.
		menu_init(
			initialized,
			input_allowed,
			MC_COUNT,
			main_unput_and_put,
			(MENU_OPTION_LEFT - 32),
			(MENU_OPTION_W + 64),
			option_choice_top(OC_COUNT)
		);
	}

	if(!key_det) {
		input_allowed = true;
	}
	if(!input_allowed) {
		return;
	}
	menu_update_vertical(key_det, MC_COUNT);

	if((key_det & INPUT_OK) || (key_det & INPUT_SHOT)) {
		snd_se_play_force(11);
		switch(menu_sel) {
		case MC_GAME:
			start_game();
			return_from_other_screen_to_main(initialized, MC_GAME);
			return;
		case MC_EXTRA:
			start_extra();
			return_from_other_screen_to_main(initialized, MC_EXTRA);
			return;
		case MC_REGIST_VIEW:
			regist_view_menu();
			initialized = false;
			break;
		case MC_MUSICROOM:
			musicroom_menu();
			main_cdg_load();

			// ZUN quirk: Moving to MC_GAME in TH04?
			return_from_other_screen_to_main(
				initialized, ((GAME == 5) ? MC_MUSICROOM : MC_GAME)
			);
			return;
		case MC_OPTION:
			initialized = false;
			in_option = true;
			menu_sel = OC_RANK;
			break;
		case MC_QUIT:
			initialized = false; // We're quitting anyway...
			quit = true;
			break;
		}
	}
	if(key_det & INPUT_CANCEL) {
		quit = true;
	}
	if(key_det) {
		input_allowed = false;
	}
}

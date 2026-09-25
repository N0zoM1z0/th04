bool16 near playchar_menu(void)
{
	int rank;
	int playchar;
	uint8_t input_prev;
	bool extra_unlocked;

	if(resident->stage == STAGE_EXTRA) {
		for(playchar = PLAYCHAR_REIMU; playchar < PLAYCHAR_COUNT; playchar++) {
			#define set_selectable_with(playchar, shottype, flag) \
				extra_unlocked = false; \
				for(rank = RANK_NORMAL; rank < RANK_EXTRA; rank++) { \
					extra_unlocked |= cleared_with[playchar][rank] & flag; \
				} \
				selectable_with[playchar][shottype] = (extra_unlocked != false);

			set_selectable_with(playchar, SHOTTYPE_A, SCOREDAT_CLEARED_A);
			set_selectable_with(playchar, SHOTTYPE_B, SCOREDAT_CLEARED_B);

			#undef set_selectable_with
		}
	} else {
		selectable_with[PLAYCHAR_REIMU][SHOTTYPE_A] = true;
		selectable_with[PLAYCHAR_REIMU][SHOTTYPE_B] = true;
		selectable_with[PLAYCHAR_MARISA][SHOTTYPE_A] = true;
		selectable_with[PLAYCHAR_MARISA][SHOTTYPE_B] = true;
	}

	playchar_menu_sel = (
		selectable_with[PLAYCHAR_REIMU][SHOTTYPE_A] ||
		selectable_with[PLAYCHAR_REIMU][SHOTTYPE_B]
	)
		? PLAYCHAR_REIMU
		: PLAYCHAR_MARISA;

	while(1) {
		playchar_menu_put_initial();

		// Character
		while(1) {
			input_reset_sense();
			if(input_prev == INPUT_NONE) {
				if((key_det & INPUT_LEFT) || (key_det & INPUT_RIGHT)) {
					snd_se_play_force(1);
					playchar_menu_sel = (1 - playchar_menu_sel);
					if(
						!selectable_with[playchar_menu_sel][SHOTTYPE_A] &&
						!selectable_with[playchar_menu_sel][SHOTTYPE_B]
					) {
						playchar_menu_sel = (1 - playchar_menu_sel);
					}
					graph_accesspage(1);
					pic_put();
					sync_pages_and_delay();
				}
				if((key_det & INPUT_OK) || (key_det & INPUT_SHOT)) {
					snd_se_play_force(11);
					shottype_menu_sel = (
						selectable_with[playchar_menu_sel][SHOTTYPE_A]
					)
						? SHOTTYPE_A
						: SHOTTYPE_B;

					graph_accesspage(1);
					palette_settone(200);
					pi_put_8(0, 0, 0);
					shottype_menu_put_initial();
					graph_copy_page(0);
					palette_white_in(1);
					break;
				}
				if(key_det & INPUT_CANCEL) {
					return playchar_menu_leave(true);
				}
				input_prev = key_det;
			} else {
				if(key_det == INPUT_NONE) {
					input_prev = INPUT_NONE;
				}
			}
			frame_delay(1);
		}

		// Shot type
		while(1) {
			input_reset_sense();
			if(input_prev == INPUT_NONE) {
				if((key_det & INPUT_UP) || (key_det & INPUT_DOWN)) {
					shottype_menu_sel = (1 - shottype_menu_sel);
					if(!selectable_with[playchar_menu_sel][shottype_menu_sel]) {
						shottype_menu_sel = (1 - shottype_menu_sel);
					}
					graph_accesspage(1);
					shottype_titles_put(shottype_menu_sel);
					sync_pages_and_delay();
					snd_se_play_force(1);
				}
				if((key_det & INPUT_OK) || (key_det & INPUT_SHOT)) {
					snd_se_play_force(11);
					resident->shottype = shottype_menu_sel;
					resident->playchar_ascii = (playchar_menu_sel + '0');
					return playchar_menu_leave(false);
				}
				if(key_det & INPUT_CANCEL) {
					raise_bg_free();
					pi_free(0);
					break;
				}
				input_prev = key_det;
			} else {
				if(key_det == INPUT_NONE) {
					input_prev = INPUT_NONE;
				}
			}
			frame_delay(1);
		}
	}
}

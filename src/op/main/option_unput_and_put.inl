void pascal near option_unput_and_put(int sel, vc2 col)
{
	int desc_id;
	screen_x_t cursor_left_left = OPTION_CURSOR_LEFT_LEFT;
	int cdg_value; // ACTUAL TYPE: op_cdg_slot_t

	// ZUN bloat: option_choice_top() handles both cases.
	screen_y_t top = (MENU_TOP + (sel * LABEL_H));
	if(sel == OC_QUIT) {
		top = option_choice_top(OC_QUIT);
	}

	egc_copy_rect_1_to_0_16(MENU_OPTION_LEFT, top, MENU_OPTION_W, LABEL_H);
	grcg_setcolor(GC_RMW, col);

	switch(sel) {
	case OC_RANK:
		option_label_put(OC_RANK, CDG_OPTION_LABEL_RANK);
		option_value_put(OC_RANK, (CDG_OPTION_VALUE_RANK + resident->rank));
		desc_id = (6 + resident->rank);
		break;
	case OC_LIVES:
		option_label_put(OC_LIVES, CDG_OPTION_LABEL_LIVES);
		option_value_put(OC_LIVES, (CDG_NUMERAL + resident->cfg_lives));
		desc_id = 10;
		break;
	case OC_BOMBS:
		option_label_put(OC_BOMBS, CDG_OPTION_LABEL_BOMBS);
		option_value_put(OC_BOMBS, (CDG_NUMERAL + resident->cfg_bombs));
		desc_id = 11;
		break;
	case OC_BGM:
		option_label_put(OC_BGM, CDG_OPTION_LABEL_BGM);
		cdg_value = ((resident->bgm_mode == SND_BGM_OFF)
			? CDG_OPTION_VALUE_OFF
			: (CDG_OPTION_VALUE_BGM - SND_BGM_FM26 + resident->bgm_mode)
		);
		option_value_put(OC_BGM, cdg_value);
		desc_id = (12 + resident->bgm_mode);
		break;
	case OC_SE:
		option_label_put(OC_SE, CDG_OPTION_LABEL_SE);
		cdg_value = ((resident->se_mode == SND_SE_OFF)
			? CDG_OPTION_VALUE_OFF
			: (CDG_OPTION_VALUE_SE_FM + SND_SE_FM - resident->se_mode)
		);
		option_value_put(OC_SE, cdg_value);
		desc_id = (15 + resident->se_mode);
		break;
	case OC_TURBO_OR_SLOW:
		command_put(
			option_choice_top(OC_TURBO_OR_SLOW),
			(CDG_OPTION_SLOW - resident->turbo_mode)
		);
		cursor_left_left = COMMAND_CURSOR_LEFT_LEFT;
		desc_id = (18 + resident->turbo_mode);
		break;
	case OC_RESET:
		command_put(option_choice_top(OC_RESET), CDG_OPTION_RESET);
		cursor_left_left = COMMAND_CURSOR_LEFT_LEFT;
		desc_id = 20;
		break;
	case OC_QUIT:
		command_put(option_choice_top(OC_QUIT), CDG_QUIT);
		cursor_left_left = COMMAND_CURSOR_LEFT_LEFT;
		desc_id = 21;
		break;
	}
	grcg_off();

	if(col == COL_ACTIVE) {
		cdg_put_8(cursor_left_left, top, CDG_CURSOR_LEFT);
		if(cursor_left_left == COMMAND_CURSOR_LEFT_LEFT) {
			cdg_put_8(
				(cursor_left_left + (COMMAND_CURSOR_LEFT_RIGHT_DISTANCE)),
				top,
				CDG_CURSOR_RIGHT
			);
		} else {
			cdg_put_8(OPTION_CURSOR_RIGHT_LEFT, top, CDG_CURSOR_RIGHT);
		}
		desc_unput_and_put(desc_id);
	}
}

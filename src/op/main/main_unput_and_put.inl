void pascal near main_unput_and_put(int sel, vc2 col)
{
	screen_y_t top = main_choice_top(sel);
	egc_copy_rect_1_to_0_16(MENU_MAIN_LEFT, top, MENU_MAIN_W, LABEL_H);
	grcg_setcolor(GC_RMW, col);
	int desc_id = sel;

	// ZUN bloat: Could have been deduplicated.
	switch(sel) {
	case MC_GAME:
		command_put(main_choice_top(MC_GAME), CDG_MAIN_GAME);
		desc_id = (22 + resident->rank);
		break;
	case MC_EXTRA:
		if(!extra_unlocked) {
			grcg_setcolor(GC_RMW, COL_LOCKED);
		}
		command_put(main_choice_top(MC_EXTRA), CDG_MAIN_EXTRA);
		break;
	case MC_REGIST_VIEW:
		command_put(main_choice_top(MC_REGIST_VIEW), CDG_MAIN_REGIST_VIEW);
		break;
	case MC_MUSICROOM:
		command_put(main_choice_top(MC_MUSICROOM), CDG_MAIN_MUSICROOM);
		break;
	case MC_OPTION:
		command_put(main_choice_top(MC_OPTION), CDG_MAIN_OPTION);
		break;
	case MC_QUIT:
		command_put(main_choice_top(MC_QUIT), CDG_QUIT);
		break;
	}
	grcg_off();

	if(col == COL_ACTIVE) {
		cdg_put_8(COMMAND_CURSOR_LEFT_LEFT,  top, CDG_CURSOR_LEFT);
		cdg_put_8(COMMAND_CURSOR_RIGHT_LEFT, top, CDG_CURSOR_RIGHT);
		desc_unput_and_put(desc_id);
	}
}

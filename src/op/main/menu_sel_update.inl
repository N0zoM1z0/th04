void pascal near menu_sel_update_and_render(int8_t max, int8_t direction)
{
	menu_unput_and_put(menu_sel, COL_INACTIVE);

	menu_sel += direction;
	if(menu_sel < 0) {
		menu_sel = max;
	}
	if(menu_sel > max) {
		menu_sel = 0;
	}
	if(!extra_unlocked && (menu_sel == MC_EXTRA) && !in_option) {
		menu_sel += direction;
	}

	menu_unput_and_put(menu_sel, COL_ACTIVE);
	snd_se_play_force(1);
}

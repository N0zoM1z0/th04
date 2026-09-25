void near setup_bgm_menu(void)
{
	int sel;
	setup_submenu(
		sel,
		SETUP_BGM_CAPTION,
		SND_BGM_MODE_COUNT,
		SND_BGM_FM86,
		bgm_choice_put,
		bgm_help_put,
		INPUT_UP
	);
	resident->bgm_mode = sel;
}

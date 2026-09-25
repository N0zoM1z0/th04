void near setup_se_menu(void)
{
	int sel;
	setup_submenu(
		sel,
		SETUP_SE_CAPTION,
		SND_SE_MODE_COUNT,
		SND_SE_FM,
		se_choice_put,
		se_help_put,
		INPUT_DOWN
	);
	resident->se_mode = sel;
}

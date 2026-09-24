void near start_extra(void)
{
	resident->stage = STAGE_EXTRA;
	resident->credit_lives = 3;
	resident->credit_bombs = 2;
	resident->playchar_ascii = ('0' + PLAYCHAR_REIMU);
	resident->stage_ascii = ('0' + STAGE_EXTRA);

	if(playchar_menu()) {
		return;
	}

	resident->demo_num = 0;
	main_cdg_free();
	cfg_save();
	gaiji_restore();
	snd_kaja_func(KAJA_SONG_FADE, 10);
	game_exit();
	execl(BINARY_MAIN, BINARY_MAIN, nullptr);
}

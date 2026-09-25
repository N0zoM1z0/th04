void near start_game(void)
{
	resident->stage = 0;
	resident->credit_lives = resident->cfg_lives;
	resident->credit_bombs = resident->cfg_bombs;
	resident->playchar_ascii = ('0' + PLAYCHAR_REIMU);
	resident->stage_ascii = ('0' + 0);

	if(playchar_menu()) {
		return;
	}

	resident->demo_num = 0;
	main_cdg_free();
	cfg_save();
	gaiji_restore();
	snd_kaja_func(KAJA_SONG_FADE, 10);
	game_exit();

	if(!resident->debug) {
		execl(BINARY_MAIN, BINARY_MAIN, nullptr);
	} else {
		execl(BINARY_DEB, BINARY_DEB, nullptr);
	}
}

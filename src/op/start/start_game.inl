void near start_game(void)
{
	// Seed the resident run contract before the character menu fills in the
	// final character and shot type. MAIN reads this same block after execl().
	resident->stage = 0;
	resident->credit_lives = resident->cfg_lives;
	resident->credit_bombs = resident->cfg_bombs;
	resident->playchar_ascii = ('0' + PLAYCHAR_REIMU);
	resident->stage_ascii = ('0' + 0);

	if(playchar_menu()) {
		return;
	}

	resident->demo_num = 0;

	// The following order is part of the overlay handoff: discard OP assets,
	// persist the resident segment/options, restore the text font, request the
	// music fade, and only then release OP's hardware/runtime ownership.
	main_cdg_free();
	cfg_save();
	gaiji_restore();
	snd_kaja_func(KAJA_SONG_FADE, 10);
#ifdef TH04P
	respal_free();
#endif
	game_exit();

	// Successful execl() replaces OP and never returns. A failure falls through
	// with OP already torn down; the original has no recovery path here.
	if(!resident->debug) {
		execl(GAMEPLAY_BINARY, GAMEPLAY_BINARY, nullptr);
	} else {
		execl(DEBUG_GAMEPLAY_BINARY, DEBUG_GAMEPLAY_BINARY, nullptr);
	}
}

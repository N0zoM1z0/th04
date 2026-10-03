void near start_extra(void)
{
	// Extra is represented as stage 6 in the resident contract. Its fixed
	// starting resources are written before the shared character/shot menu.
	resident->stage = STAGE_EXTRA;
	resident->credit_lives = 3;
	resident->credit_bombs = 2;
	resident->playchar_ascii = ('0' + PLAYCHAR_REIMU);
	resident->stage_ascii = ('0' + STAGE_EXTRA);

	if(playchar_menu()) {
		return;
	}

	resident->demo_num = 0;
	// Match the normal-game overlay teardown. The successful DOS exec transfers
	// control directly to MAIN; no caller in OP resumes afterward.
	main_cdg_free();
	cfg_save();
	gaiji_restore();
	snd_kaja_func(KAJA_SONG_FADE, 10);
#ifdef TH04P
	respal_free();
#endif
	game_exit();
	execl(GAMEPLAY_BINARY, GAMEPLAY_BINARY, nullptr);
}

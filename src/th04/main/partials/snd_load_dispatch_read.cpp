	if((_AH == KAJA_GET_SONG_ADDRESS) && (snd_bgm_mode == SND_BGM_MIDI)) {
		geninterrupt(MMD);
	} else {
		geninterrupt(PMD);
	}

	// DOS file read; song data address is in DS:DX
	_AX = 0x3F00;
	_CX = snd_load_size();
	geninterrupt(0x21);

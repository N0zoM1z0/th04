void pascal snd_load(const char fn[PF_FN_LEN], snd_load_func_t func)
{
	int i;

	for(i = 0; i < PF_FN_LEN; i++) {
		snd_load_fn[i] = fn[i];
	}

	i = 0;
	do {
		i++;
	} while(snd_load_fn[i] != '\0');

	snd_load_fn[i + 4] = '\0';
	snd_load_fn[i++] = '.';

	if(func == SND_LOAD_SE) {
		snd_load_fn[i + 0] = 'e';
		snd_load_fn[i + 1] = 'f';
		if(snd_se_mode == SND_SE_OFF) {
			return;
		} else if(snd_se_mode == SND_SE_BEEP) {
			snd_load_fn[i + 2] = 's';
			bgm_read_sdata(snd_load_fn);
			return;
		} else {
			snd_load_fn[i + 2] = 'c';
		}
	} else {
		if(snd_bgm_mode == SND_BGM_OFF) {
			return;
		}
		snd_kaja_func(KAJA_SONG_STOP, 0);
		snd_load_fn[i + 0] = SND_LOAD_EXT[snd_bgm_mode][0];
		snd_load_fn[i + 1] = SND_LOAD_EXT[snd_bgm_mode][1];
		snd_load_fn[i + 2] = SND_LOAD_EXT[snd_bgm_mode][2];
	}

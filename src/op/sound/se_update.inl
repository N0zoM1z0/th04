void far snd_se_update(void)
{
	if((snd_se_mode == SND_SE_OFF) || (snd_se_playing == SE_NONE)) {
		return;
	}
	if(snd_se_frame == 0) {
		_AL = snd_se_playing;
		if(snd_se_mode != SND_SE_BEEP) {
			_AH = PMD_SE_PLAY;
			geninterrupt(PMD_INTERRUPT);
		} else {
			_AH ^= _AH;
			bgm_sound(_AX);
		}
	}
	snd_se_frame++;
	if(snd_se_priority_frames[snd_se_current_index()] < snd_se_frame) {
		snd_se_frame = 0;
		snd_se_playing = SE_NONE;
	}
}

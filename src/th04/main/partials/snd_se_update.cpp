void snd_se_update(void)
{
	if(!snd_se_active() || (snd_se_playing == SE_NONE)) {
		return;
	}
	if(snd_se_frame == 0) {
		driver_play(snd_se_playing);
	}
	snd_se_frame++;
	if(snd_se_priority_frames[for_current()] < snd_se_frame) {
		snd_se_frame = 0;
		snd_se_playing = SE_NONE;
	}
}

void DEFCONV snd_se_play(int new_se)
{
	register int se = snd_get_param(new_se);
	if(!snd_se_active()) {
		return;
	}
	if(snd_se_playing == SE_NONE) {
		snd_se_playing = se;
	} else if(snd_se_priorities[for_current()] <= snd_se_priorities[se]) {
		snd_se_playing = se;
		snd_se_frame = 0;
	}
}

#pragma option -zCSHARED -k-

extern unsigned char snd_se_mode;
extern unsigned char snd_se_playing;
extern unsigned char snd_se_frame;
extern unsigned char snd_se_priorities[];

static const unsigned char SE_NONE = 0xFF;

void far pascal snd_se_play(int new_se)
{
	if(!snd_se_mode) {
		return;
	}
	if(snd_se_playing == SE_NONE) {
		snd_se_playing = new_se;
	} else if(snd_se_priorities[snd_se_playing] <= snd_se_priorities[new_se]) {
		snd_se_playing = new_se;
		snd_se_frame = 0;
	}
}

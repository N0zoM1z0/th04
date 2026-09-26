#pragma option -zCSHARED -k-

#include "src/shared/sound/api.hpp"
#include "src/shared/sound/impl.hpp"

void far pascal snd_se_play(int new_se)
{
	register int se = snd_get_param(new_se);
	if(!snd_se_mode) {
		return;
	}
	if(snd_se_playing == SE_NONE) {
		snd_se_playing = se;
	} else if(snd_se_priorities[snd_se_current_index()] <= snd_se_priorities[se]) {
		snd_se_playing = se;
		snd_se_frame = 0;
	}
}

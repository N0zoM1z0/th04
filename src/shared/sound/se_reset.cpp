#pragma option -zCSHARED -WX -k-

#include "src/shared/sound/api.hpp"
#include "src/shared/sound/impl.hpp"

void snd_se_reset(void)
{
	snd_se_frame = 0;
	snd_se_playing = SE_NONE;
}
#pragma codestring "\x90"

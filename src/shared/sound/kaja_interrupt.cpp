#pragma option -zCSHARED
#include "src/shared/sound/api.hpp"
#include "compat/rec98/th02/snd/impl.hpp"

int16_t pascal snd_kaja_interrupt(int16_t ax)
{
	if(!snd_bgm_active()) {
		return _AX;
	}

	// TH04 should use snd_get_param() here, but doesn't....
#if (GAME == 5)
	_AX = snd_get_param(ax);
#else
	_AX = ax;
#endif

	if(snd_bgm_is_fm()) {
		geninterrupt(PMD);
	} else {
		geninterrupt(MMD);
	}
	return _AX;
}

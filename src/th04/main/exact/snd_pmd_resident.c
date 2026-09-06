#pragma option -zCSHARED -k-

#include "x86real.h"
#include "th04/snd/snd.h"

bool16 snd_pmd_resident(void)
{
	_AX = 0;
	snd_interrupt_if_midi = PMD;
	snd_midi_possible = _AX;
	snd_bgm_mode = _AX;
	snd_se_mode = _AX;

	_ES = _AX;
	if(kaja_isr_magic_matches(*(void far * __es *)(PMD * 4), 'P', 'M', 'D')) {
		_AX++;
	}
	return _AX;
}

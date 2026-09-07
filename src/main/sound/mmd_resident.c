#pragma option -WX -zCSHARED -k-

#include "x86real.h"
#include "th04/snd/snd.h"

bool16 snd_mmd_resident(void)
{
	_ES = 0;
	if(kaja_isr_magic_matches(*(void far * __es *)(MMD * 4), 'M', 'M', 'D')) {
		snd_interrupt_if_midi = MMD;
		snd_midi_possible = true;
		return true;
	}
	return false;
}

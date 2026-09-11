#pragma option -zCMAIN_012_TEXT -zPmain_01 -k-

#include "compat/rec98/th04/main/player/shot.hpp"

Shot near * near shots_add(void)
{
	#define shot reinterpret_cast<Shot near *>(_BX)
	#define ret reinterpret_cast<Shot near *>(_AX)

	ret = 0;
	for(;;) {
		if(static_cast<uint8_t>(shot_last_id) >= SHOT_COUNT) {
			return ret;
		}
		shot = shot_ptr;
		shot_ptr++;
		if(shot->flag != SF_FREE) {
			shot_last_id++;
			continue;
		}
		reinterpret_cast<uint16_t near &>(shot->flag) = SF_ALIVE;
		shot->pos.cur = player_pos.cur;
		shot->pos.velocity.set_long(0, TO_SP(-12));
		ret = shot;
		return ret;
	}

	#undef ret
	#undef shot
}

#pragma option -k.

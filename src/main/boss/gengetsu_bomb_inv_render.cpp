#pragma option -zCMAIN_01_TEXT -zPmain_01

#include "compat/rec98/libs/master.lib/pc98_gfx.hpp"
#include "th04/main/boss/boss.hpp"

extern unsigned char boss_bomb_invincibility_frames;

extern "C" void near gengetsu_bomb_inv_render(void)
{
    register int left;
    #define top _DI

    if(boss_bomb_invincibility_frames != 0) {
        if(
            (boss_bomb_invincibility_frames >= 0x20) ||
            ((boss_bomb_invincibility_frames & 1) != 0)
        ) {
            left = ((boss.pos.cur.x.v >> 4) - 15);
            top = ((boss.pos.cur.y.v >> 4) - 32);
            super_put(left, _AX, 136);
            super_put((left + 48), top, 137);
        }
    }

    #undef top
}

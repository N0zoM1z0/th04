#pragma option -zCMAIN_036_TEXT -zPmain_03
#include "th04/main/boss/boss.hpp"

extern unsigned char gengetsu_wave_amp;

extern "C" bool near gengetsu_wave_bounce(void)
{
    if(boss.phase_frame == 1) {
        boss.pos.velocity.x.v = (
            (boss.pos.cur.x.v < TO_SP(192)) ? TO_SP(2) : -TO_SP(2)
        );
    }

    if(
        ((boss.pos.velocity.x.v < 0) && (boss.pos.cur.x.v >= TO_SP(193))) ||
        ((boss.pos.velocity.x.v > 0) && (boss.pos.cur.x.v <= TO_SP(192)))
    ) {
        boss.pos.cur.x.v += boss.pos.velocity.x.v;
    }

    if(boss.phase_frame <= 64) {
        gengetsu_wave_amp++;
    } else {
        gengetsu_wave_amp--;
    }

    if(boss.phase_frame == 128) {
        boss.pos.cur.x.v = TO_SP(192);
        gengetsu_wave_amp = 0;
        return true;
    }
    return false;
}

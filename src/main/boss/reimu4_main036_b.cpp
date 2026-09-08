#pragma option -zCMAIN_036_TEXT -zPmain_03

#include "th04/main/boss/boss.hpp"

extern unsigned char reimu_trail_visible;

extern "C" void near reimu_phase_move_b(void)
{
    register int duration;

    if(boss.phase_frame == 1) {
        reimu_trail_visible = 1;
        if((boss.phase_state.patterns_seen % 3) == 0) {
            boss.pos.velocity.x.v = TO_SP(4);
            boss.pos.velocity.y.v = TO_SP(-1);
        } else if((boss.phase_state.patterns_seen % 3) == 1) {
            boss.pos.velocity.x.v = TO_SP(-4);
            boss.pos.velocity.y.v = 0;
        } else {
            boss.pos.velocity.x.v = TO_SP(4);
            boss.pos.velocity.y.v = TO_SP(1);
        }
    }

    boss.pos.update_seg3();

    duration = 32;
    if((boss.phase_state.patterns_seen % 3) == 1) {
        duration = 64;
    }
    if(boss.phase_frame == duration) {
        boss.phase_state.patterns_seen++;
        boss.mode = (boss.phase_state.patterns_seen % 2);
        boss.phase_frame = 0;
        reimu_trail_visible = 0;
    }
}

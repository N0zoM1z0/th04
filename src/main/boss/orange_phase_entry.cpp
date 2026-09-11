#pragma option -zCMAIN_033_TEXT -zPmain_03

#include "compat/rec98/th02/v_colors.hpp"
#include "compat/rec98/th03/math/randring.hpp"
#include "th04/main/boss/boss.hpp"
#include "th04/main/gather.hpp"
#include "th04/main/circle.hpp"

extern "C" int near orange_phase_entry(void)
{
    subpixel_t target_x;
    subpixel_t target_y;

    gather_add_only_3stack((boss.phase_frame - 70), 7, 6);
    if(boss.phase_frame < 16) {
        return 1;
    }
    if(boss.phase_frame == 16) {
        target_x = (randring2_next16_mod(TO_SP(320)) + TO_SP(32));
        target_y = (randring2_next16_mod(TO_SP(96)) + TO_SP(64));
        boss.pos.velocity.x.v = (
            (target_x - boss.pos.cur.x.v) / TO_SP(4)
        );
        boss.pos.velocity.y.v = (
            (target_y - boss.pos.cur.y.v) / TO_SP(4)
        );
        gather_template.radius.v = TO_SP(96);
        gather_template.ring_points = 8;
    }
    if(boss.phase_frame < 70) {
        boss.pos.update_seg3();
        goto ret0;
    }
    if(boss.phase_frame == 70) {
        circles_add_shrinking(boss.pos.cur.x.v, boss.pos.cur.y.v);
        circles_color = V_WHITE;
        goto ret0;
    }
    if(boss.phase_frame < 86) {
        return 1;
    }
    return 2;

ret0:
    return 0;
}

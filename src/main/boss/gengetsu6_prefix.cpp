#pragma option -zCMAIN_036_TEXT -zPmain_03
#include "compat/rec98/th02/v_colors.hpp"
#include "th04/main/boss/boss.hpp"
#include "th04/main/gather.hpp"
#include "th04/main/circle.hpp"
#pragma option -a2

extern unsigned char gengetsu_wave_amp;
extern Subpixel gengetsu_wave_target_x;

extern "C" void near gengetsu_gathers_add_dual(void)
{
    gather_template.angle_delta = -2;
    gather_add_only();
    gather_template.angle_delta = 2;
    gather_add_only();
}

extern "C" void near gengetsu_gather_intro(void)
{
    switch(boss.phase_frame) {
    case 0x30:
        gather_template.radius.v = TO_SP(320);
        gather_template.center.y.v = (boss.pos.cur.y.v - TO_SP(48));
        gather_template.center.x.v = (boss.pos.cur.x.v - TO_SP(13));
        gather_template.ring_points = 16;
        gather_template.col = V_WHITE;
    add_gathers:
        gengetsu_gathers_add_dual();
        return;
    case 0x32:
        gather_template.col = 9;
        goto add_gathers;
    case 0x34:
        goto add_gathers;
    case 0x40:
        circles_add_shrinking(gather_template.center.x.v, gather_template.center.y.v);
        circles_color = V_WHITE;
        return;
    default:
        return;
    }
}

extern "C" bool near gengetsu_wave_step(void)
{
    if(boss.phase_frame == 1) {
        boss.pos.velocity.x.v = (
            (gengetsu_wave_target_x.v - boss.pos.cur.x.v) / 64
        );
    }
    boss.pos.cur.x.v += boss.pos.velocity.x.v;
    if(boss.phase_frame <= 32) {
        gengetsu_wave_amp += 2;
    } else {
        gengetsu_wave_amp += -2;
    }
    if(boss.phase_frame == 64) {
        gengetsu_wave_amp = 0;
        return true;
    }
    return false;
}

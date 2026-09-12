#ifndef TH04_MUGETSU_MAIN033_COMBINED
#pragma option -zCMAIN_033_TEXT -zPmain_03
#include "compat/rec98/th02/v_colors.hpp"
#include "th04/main/boss/boss.hpp"
#include "th04/main/gather.hpp"
#include "th04/main/circle.hpp"
#pragma option -a2
#endif

extern int mugetsu_gather_frame_offset;
extern SPPoint mugetsu_anchor;

extern "C" void near mugetsu_gathers_add_dual(void)
{
    gather_template.angle_delta = -2;
    gather_add_only();
    gather_template.angle_delta = 2;
    gather_add_only();
}

extern "C" void near mugetsu_gather_intro(void)
{
    switch(boss.phase_frame + mugetsu_gather_frame_offset) {
    case 0x20:
        gather_template.radius.v = TO_SP(320);
        gather_template.center.y.v = (mugetsu_anchor.y.v - TO_SP(10));
        gather_template.center.x.v = mugetsu_anchor.x.v;
        gather_template.ring_points = 16;
        gather_template.col = 14;
    add_gathers:
        mugetsu_gathers_add_dual();
        return;
    case 0x22:
        gather_template.col = 7;
        goto add_gathers;
    case 0x24:
        goto add_gathers;
    case 0x30:
        circles_add_shrinking(gather_template.center.x.v, gather_template.center.y.v);
        circles_color = V_WHITE;
        return;
    default:
        return;
    }
}

#ifndef TH04_ELLY_MAIN034_COMBINED
#pragma option -a
#pragma option -zCMAIN_034_TEXT -zPmain_03

#include "compat/rec98/th02/v_colors.hpp"
#include "th04/main/gather.hpp"
#include "th04/main/circle.hpp"
#include "th04/main/boss/boss.hpp"

#endif

extern "C" unsigned char near elly_gather_update(void)
{
    if(boss.phase_frame > 32) {
        return 0;
    }

    switch(boss.phase_frame) {
    case 1:
        gather_template.center.x.v = boss.pos.cur.x.v;
        gather_template.center.y.v = boss.pos.cur.y.v;
        gather_template.ring_points = 8;
        gather_template.radius.v = TO_SP(192);
        gather_template.col = V_WHITE;
    add_gathers:
        gather_template.angle_delta = -2;
        gather_add_only();
        gather_template.angle_delta = 2;
        gather_add_only();
        break;

    case 8:
        gather_template.col = 7;
        goto add_gathers;

    case 16:
        circles_add_shrinking(boss.pos.cur.x.v, boss.pos.cur.y.v);
        circles_color = V_WHITE;
        gather_template.col = 7;
        goto add_gathers;

    case 32:
        return 2;
    }
    return 1;
}

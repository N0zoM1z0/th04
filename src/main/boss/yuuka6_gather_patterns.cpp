#pragma option -a
#pragma option -zCMAIN_034_TEXT -zPmain_03

#include "compat/rec98/libs/master.lib/master.hpp"
#include "compat/rec98/th02/v_colors.hpp"
#include "th04/snd/snd.h"
#include "th04/main/gather.hpp"
#include "th04/main/circle.hpp"
#include "th04/main/boss/boss.hpp"

extern SPPoint yuuka6_aux_pos;

extern "C" void near y6_gather_side(void)
{
    switch(boss.phase_frame) {
    case 0x10:
        snd_se_play(8);
        gather_template.radius.v = TO_SP(320);
        gather_template.center.y.v = (boss.pos.cur.y.v - TO_SP(4));
        gather_template.center.x.v = (boss.pos.cur.x.v + TO_SP(24));
        gather_template.ring_points = 16;
        gather_template.col = 9;
        gather_template.angle_delta = -2;
        // fall through
    case 0x14:
        gather_add_only();
        gather_template.center.x.v -= TO_SP(44);
        gather_template.angle_delta = 2;
    second_side:
        gather_add_only();
        break;

    case 0x12:
        gather_template.col = 8;
        gather_add_only();
        gather_template.center.x.v += TO_SP(44);
        gather_template.angle_delta = -2;
        goto second_side;

    case 0x20:
        circles_add_shrinking(
            gather_template.center.x.v,
            gather_template.center.y.v
        );
        circles_add_shrinking(
            (gather_template.center.x.v + TO_SP(44)),
            gather_template.center.y.v
        );
        circles_color = V_WHITE;
        break;
    }
}

static void near y6_gather_pair(void)
{
    gather_template.angle_delta = -2;
    gather_add_only();
    gather_template.angle_delta = 2;
    gather_add_only();
}

extern "C" void near y6_gather_center(void)
{
    switch(boss.phase_frame) {
    case 0x30:
        snd_se_play(8);
        gather_template.radius.v = TO_SP(320);
        gather_template.center.y.v = (boss.pos.cur.y.v + TO_SP(32));
        gather_template.center.x.v = boss.pos.cur.x.v;
        gather_template.ring_points = 8;
        gather_template.col = 9;
        // fall through
    case 0x34:
    add_center:
        y6_gather_pair();
        break;

    case 0x32:
        gather_template.col = 8;
        goto add_center;

    case 0x40:
        circles_add_shrinking(
            gather_template.center.x.v,
            gather_template.center.y.v
        );
        circles_color = V_WHITE;
        break;
    }
}

extern "C" void near y6_gather_dual(void)
{
    switch(boss.phase_frame) {
    case 0x20:
        snd_se_play(8);
        gather_template.radius.v = TO_SP(320);
        gather_template.ring_points = 8;
        gather_template.col = 9;
        // fall through
    case 0x24:
    add_dual:
        gather_template.center.y.v = (boss.pos.cur.y.v + TO_SP(32));
        gather_template.center.x.v = boss.pos.cur.x.v;
        y6_gather_pair();
        gather_template.center.y.v = (yuuka6_aux_pos.y.v + TO_SP(32));
        gather_template.center.x.v = yuuka6_aux_pos.x.v;
        y6_gather_pair();
        break;

    case 0x22:
        gather_template.col = 8;
        goto add_dual;

    case 0x30:
        circles_add_shrinking(
            boss.pos.cur.x.v,
            (boss.pos.cur.y.v + TO_SP(32))
        );
        circles_add_shrinking(
            yuuka6_aux_pos.x.v,
            (yuuka6_aux_pos.y.v + TO_SP(32))
        );
        circles_color = V_WHITE;
        break;
    }
}

extern "C" void near y6_gather_self(void)
{
    switch(boss.phase_frame) {
    case 0x10:
        snd_se_play(8);
        gather_template.radius.v = TO_SP(320);
        gather_template.center.y.v = boss.pos.cur.y.v;
        gather_template.center.x.v = boss.pos.cur.x.v;
        gather_template.ring_points = 16;
        gather_template.col = 7;
        // fall through
    case 0x14:
    add_self:
        y6_gather_pair();
        break;

    case 0x12:
        gather_template.col = 6;
        goto add_self;

    case 0x20:
        circles_add_shrinking(
            gather_template.center.x.v,
            gather_template.center.y.v
        );
        circles_color = V_WHITE;
        break;
    }
}

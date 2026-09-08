#pragma option -zCMAIN_036_TEXT -zPmain_03

#include "compat/rec98/th02/v_colors.hpp"
#include "th04/main/gather.hpp"
#include "th04/main/circle.hpp"
#include "th04/main/boss/boss.hpp"
#include "th04/snd/snd.h"

#pragma option -a

extern "C" unsigned char near reimu_gather_intro(void)
{
    switch(boss.phase_frame) {
    case 14:
        gather_template.center.x.v = (boss.pos.cur.x.v + TO_SP(4));
        gather_template.center.y.v = (boss.pos.cur.y.v - TO_SP(28));
        gather_template.ring_points = 16;
        gather_template.radius.v = TO_SP(256);
        gather_template.col = 9;
        gather_add_only();
        boss.sprite = 129;
        snd_se_play(8);
        circles_color = V_WHITE;
        break;

    case 16:
        gather_template.col = 8;
    case 18:
        gather_add_only();
        break;

    case 22:
        boss.sprite = 130;
        break;

    case 26:
        boss.sprite = 131;
        break;

    case 30:
        boss.sprite = 132;
        circles_add_shrinking(
            gather_template.center.x.v,
            gather_template.center.y.v
        );
        break;

    case 34:
        boss.sprite = 133;
        break;

    case 38:
        boss.sprite = 134;
        break;

    case 42:
        boss.sprite = 135;
        break;

    case 46:
        boss.sprite = 129;
        snd_se_play(3);
        return 2;
    }

    if(boss.phase_frame < 46) {
        return 0;
    }
    return 1;
}

#pragma option -zCMAIN_036_TEXT -zPmain_03

#include "compat/rec98/libs/master.lib/master.hpp"
#include "th04/sprites/main_pat.h"
#include "th04/main/bullet/bullet.hpp"
#include "th04/main/boss/boss.hpp"
#include "th04/main/player/player.hpp"
#include "th04/snd/snd.h"

extern "C" unsigned char near reimu_gather_intro(void);
extern signed char reimu_pattern_angle_delta;

extern "C" void near reimu_phase_spread_yellow(void)
{
    unsigned char state = reimu_gather_intro();

    if(state == 2) {
        bullet_template.spawn_type = BST_BULLET16;
        bullet_template.patnum = PAT_BULLET16_D_YELLOW;
        bullet_template.speed.v = TO_SP(6);
        boss.angle = iatan2(
            (player_pos.cur.y.v - boss.pos.cur.y.v),
            (player_pos.cur.x.v - boss.pos.cur.x.v)
        );
        bullet_template.group = BG_SPREAD;
        bullet_template.count = 6;
        bullet_template.delta.spread_angle = boss_statebyte[5];
        bullet_template_tune();
        reimu_pattern_angle_delta = (
            (player_pos.cur.x.v < TO_SP(192)) ? -2 : 2
        );
    }

    if(state == 1) {
        if((boss.phase_frame % 4) == 0) {
            bullet_template.angle = boss.angle;
            bullets_add_regular();
            snd_se_play(3);
            if(boss.phase_frame >= 64) {
                boss.angle += reimu_pattern_angle_delta;
            }
        }
        if(boss.phase_frame >= 112) {
            boss.sprite = 128;
            boss.phase_frame = 0;
            boss.mode = -1;
        }
    }
}

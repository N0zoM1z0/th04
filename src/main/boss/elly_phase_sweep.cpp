#ifndef TH04_ELLY_MAIN034_COMBINED
#pragma option -zCMAIN_034_TEXT -zPmain_03

#include "compat/rec98/libs/master.lib/master.hpp"
#include "th04/snd/snd.h"
#ifndef TH04_ELLY_MAIN034_COMBINED
#include "th04/main/bullet/bullet.hpp"
#endif
#include "th04/main/boss/boss.hpp"
#include "th04/main/player/player.hpp"

#pragma option -a

#endif

extern "C" unsigned char near elly_gather_update(void);
extern "C" void near elly_phase_burst(void);

extern "C" void near elly_phase_sweep(void)
{
    switch(elly_gather_update()) {
    case 0:
        break;
    case 2:
        bullet_template.angle = (
            iatan2(
                (player_pos.cur.y.v - boss.pos.cur.y.v),
                (player_pos.cur.x.v - boss.pos.cur.x.v)
            ) - 0x40
        );
        return;
    default:
        return;
    }

    if((boss.phase_frame % 4) == 0) {
        snd_se_play(9);
    }

    if(boss.phase_frame < 72) {
        if((boss.phase_frame % 2) != 0) {
            return;
        }
        bullet_template.spawn_type = BST_PELLET;
        bullet_template.speed.v = TO_SP(4);
        bullet_template.group = BG_SPREAD;
        bullet_template.count = 2;
        bullet_template.delta.spread_angle = 0x0C;
        bullet_template_tune();
        bullets_add_regular();
        bullet_template.angle += 4;
        return;
    }

    if(boss.phase_frame == 72) {
        bullet_template.angle += 0x40;
        return;
    }

    if(boss.phase_frame < 144) {
        if((boss.phase_frame % 2) != 0) {
            return;
        }
        bullet_template.spawn_type = BST_PELLET;
        bullet_template.speed.v = TO_SP(4);
        bullet_template.group = BG_SPREAD;
        bullet_template.count = 2;
        bullet_template.delta.spread_angle = 0x0C;
        bullet_template_tune();
        bullets_add_regular();
        bullet_template.angle -= 2;
        return;
    }

    if(boss.phase_frame >= 144) {
        elly_phase_burst();
    }
}

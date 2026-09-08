#pragma option -zCMAIN_036_TEXT -zPmain_03
#include "compat/rec98/libs/master.lib/master.hpp"
#include "th04/sprites/main_pat.h"
#include "th04/main/frames.h"
#include "th04/main/boss/boss.hpp"
#include "th04/main/bullet/bullet.hpp"
#include "th04/main/player/player.hpp"
#include "th04/snd/snd.h"

extern "C" unsigned char near gengetsu_phase_state(void);

extern "C" void near gengetsu_aimed_spread_phase(void)
{
    switch(gengetsu_phase_state()) {
    case 2:
        bullet_template.speed.v = TO_SP(5);
        bullet_template.group = BG_SPREAD;
        bullet_template.count = 1;
        bullet_template.delta.spread_angle = 6;
        bullet_template.angle = iatan2(
            (player_pos.cur.y.v - bullet_template.origin.y.v),
            (player_pos.cur.x.v - bullet_template.origin.x.v)
        );
        return;
    case 3:
        if(stage_frame_mod4 != 0) return;
        bullets_add_regular();
        bullet_template.count++;
        snd_se_play(9);
        return;
    case 4:
        boss.phase_frame = 0;
        boss.mode = -1;
        return;
    }
}

extern "C" void near gengetsu_mirror_spread_phase(void)
{
    switch(gengetsu_phase_state()) {
    case 2:
        bullet_template.patnum = PAT_BULLET16_D_BLUE;
        bullet_template.group = BG_SPREAD;
        bullet_template.count = 5;
        bullet_template.delta.spread_angle = 0x0B;
        bullet_template.angle = 0;
        bullet_template.speed.v = (TO_SP(5) + 10);
        return;
    case 3:
        if(stage_frame_mod2 != 0) return;
        bullet_template.spawn_type = BST_BULLET16;
        bullets_add_regular();
        bullet_template.angle = static_cast<unsigned char>(0x80 - bullet_template.angle);
        bullets_add_regular();
        bullet_template.angle = static_cast<unsigned char>(0x78 - bullet_template.angle);
        snd_se_play(3);
        return;
    case 4:
        boss.phase_frame = 0;
        boss.mode = -1;
        return;
    }
}

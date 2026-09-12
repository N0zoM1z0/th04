#pragma option -zCMAIN_033_TEXT -zPmain_03
#include "compat/rec98/libs/master.lib/master.hpp"
#include "th04/sprites/main_pat.h"
#include "th04/main/frames.h"
#include "th04/main/boss/boss.hpp"
#include "th04/main/bullet/bullet.hpp"
#include "th04/main/player/player.hpp"
#include "th04/math/randring.hpp"
#include "th04/snd/snd.h"

extern unsigned char bullet_special_turns_max;
extern unsigned char (near *mugetsu_transition_func)(void);

extern "C" void near mugetsu_18314(void)
{
    switch(mugetsu_transition_func()) {
    case 1:
        bullet_template.group = BG_RING;
        bullet_template.count = 8;
        bullet_template.speed.v = TO_SP(2);
        bullet_template.angle = randring2_next16();
        boss_statebyte[15] = randring2_next16_and(1);
        return;
    case 2:
        if(stage_frame_mod4 != 0) return;
        bullets_add_regular();
        bullet_template.speed.v += 3;
        if(boss_statebyte[15] != 0) {
            _AL = 4;
        } else {
            _AL = -4;
        }
        _AL += bullet_template.angle;
        bullet_template.angle = _AL;
        snd_se_play(3);
        return;
    case 3:
        boss.phase_frame = 0;
        boss.mode = -1;
        return;
    }
}

extern "C" void near mugetsu_1838A(void)
{
    volatile int frame_mod8;

    switch(mugetsu_transition_func()) {
    case 1:
        snd_se_play(15);
        bullet_template.spawn_type = BST_BULLET16;
        bullet_template.patnum = PAT_BULLET16_N_CROSS_YELLOW;
        bullet_template.angle = 0;
        bullet_template.group = BG_RING;
        bullet_template.count = 32;
        bullet_template.special_motion = BSM_DECELERATE_THEN_TURN;
        bullet_template.speed.v = (TO_SP(2) + 8);
        bullet_special_turns_max = 2;
        bullet_template_special_angle.turn_by = -0x20;
        bullet_template_tune();
        bullets_add_special_fixedspeed();
        bullet_template_special_angle.turn_by = 0x20;
        bullets_add_special_fixedspeed();
        bullet_template.angle = iatan2(
            (player_pos.cur.y.v - boss.pos.cur.y.v),
            (player_pos.cur.x.v - boss.pos.cur.x.v)
        );
        bullet_template.delta.spread_angle = 0x42;
        return;
    case 2:
        _AX = (boss.phase_frame & 7);
        frame_mod8 = _AX;
        if(_AX == 0) {
            bullet_template.delta.spread_angle += -8;
        }
        bullet_template.spawn_type = BST_BULLET16;
        bullet_template.patnum = PAT_BULLET16_D_BLUE;
        bullet_template.speed.v = ((frame_mod8 * 12) + TO_SP(2));
        bullet_template.group = BG_SPREAD;
        bullet_template.count = 2;
        bullets_add_regular();
        if(stage_frame_mod4 != 0) return;
        snd_se_play(3);
        return;
    case 3:
        boss.phase_frame = 0;
        boss.mode = -1;
        return;
    }
}

#pragma option -zCMAIN_036_TEXT -zPmain_03
#include "th04/sprites/main_pat.h"
#include "th04/main/frames.h"
#include "th04/main/boss/boss.hpp"
#include "th04/main/bullet/bullet.hpp"
#include "th04/math/randring.hpp"
#include "th04/snd/snd.h"

extern "C" void near gengetsu_random_ring(void)
{
    boss.sprite = 128;
    if(stage_frame_mod8 != 0) {
        return;
    }

    bullet_template.angle = randring2_next16();
    bullet_template.origin.x.v = (
        randring2_next16_mod(TO_SP(64)) +
        (boss.pos.cur.x.v - TO_SP(32))
    );
    bullet_template.origin.y.v = (
        randring2_next16_mod(TO_SP(32)) +
        (boss.pos.cur.y.v - TO_SP(26))
    );
    bullet_template.group = BG_RING;
    bullet_template.count = 16;
    bullet_template.spawn_type = BST_BULLET16;
    bullet_template.patnum = PAT_BULLET16_D_BLUE;
    bullet_template.speed.v = (randring2_next16_and(0x3F) + TO_SP(1));
    bullets_add_regular();
    snd_se_play(3);
}

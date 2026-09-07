#ifndef TH04_ELLY_MAIN034_COMBINED
#pragma option -a
#pragma option -zCMAIN_034_TEXT -zPmain_03

#include "compat/rec98/libs/master.lib/master.hpp"
#include "th04/snd/snd.h"
#include "th04/main/frames.h"
#include "th04/math/vector.hpp"
#include "th04/main/boss/boss.hpp"
#include "th04/main/player/player.hpp"

#endif

extern unsigned char elly_scythe_mode;
extern unsigned char elly_scythe_flag;
extern PlayfieldMotion elly_scythe_motion;
extern unsigned int elly_scythe_frame;
extern unsigned char elly_scythe_angle;
extern unsigned char elly_scythe_speed;
extern volatile signed char elly_scythe_turn;

extern SPPoint shot_hitbox_center;
extern SPPoint shot_hitbox_radius;
extern int shots_hittest(void);

extern "C" void near elly_scythe_update(void)
{
    unsigned char target_delta;

    if(elly_scythe_flag == 2) {
        elly_scythe_flag = 0;
    }

    switch(elly_scythe_mode) {
    case 1:
        if((elly_scythe_frame < 64) && ((elly_scythe_frame & 7) == 0)) {
            boss.sprite = ((elly_scythe_frame >> 3) + 134);
        }
        if(elly_scythe_frame == 0) {
            snd_se_play(8);
            goto advance_frame;
        }
        if(elly_scythe_frame == 56) {
            snd_se_play(9);
            elly_scythe_flag = 1;
            elly_scythe_motion.cur.x.v = boss.pos.cur.x.v;
            elly_scythe_motion.cur.y.v = boss.pos.cur.y.v;
            goto advance_frame;
        }
        if(elly_scythe_frame < 64) {
            goto advance_frame;
        }
        boss.sprite = 141;
        elly_scythe_mode = 2;
        // fall through

    case 2:
        if(elly_scythe_frame < 80) {
            target_delta = iatan2(
                (player_pos.cur.y.v - elly_scythe_motion.cur.y.v),
                (player_pos.cur.x.v - elly_scythe_motion.cur.x.v)
            );
            target_delta -= elly_scythe_angle;
            if((target_delta < 0x80) && (target_delta >= 0x10)) {
                elly_scythe_turn = 1;
                goto accelerate_turn;
            }
            if((target_delta >= 0x80) && (target_delta <= 0xF0)) {
                elly_scythe_turn = -1;
            accelerate_turn:
                elly_scythe_speed += stage_frame_mod2;
                goto apply_turn;
            }
            elly_scythe_speed = (elly_scythe_speed + 1);
            elly_scythe_turn = 0;
        apply_turn:
            elly_scythe_angle += elly_scythe_turn;
            goto boundary_check;
        }
        elly_scythe_speed += stage_frame_mod2;

    boundary_check:
        if(elly_scythe_motion.cur.x.v <= TO_SP(64)) {
            elly_scythe_mode = 3;
            goto advance_frame;
        }
        if(elly_scythe_motion.cur.x.v >= TO_SP(320)) {
            elly_scythe_mode = 4;
            goto advance_frame;
        }
        if(elly_scythe_motion.cur.y.v >= TO_SP(304)) {
            elly_scythe_mode = 5;
            goto advance_frame;
        }
        if(elly_scythe_motion.cur.y.v <= TO_SP(32)) {
            elly_scythe_mode = 6;
        }
        goto advance_frame;

    case 3:
        elly_scythe_speed -= 4;
        elly_scythe_angle += elly_scythe_turn;
        if(elly_scythe_speed <= 4) {
            goto begin_return;
        }
        break;

    case 4:
        elly_scythe_speed -= 4;
        elly_scythe_angle += elly_scythe_turn;
        if(elly_scythe_turn != 0) {
            elly_scythe_angle += elly_scythe_turn;
        } else {
            elly_scythe_angle++;
        }
        if(elly_scythe_speed <= 4) {
            goto begin_return;
        }
        break;

    case 5:
        elly_scythe_speed -= 4;
        elly_scythe_angle += elly_scythe_turn;
        if(elly_scythe_speed <= 4) {
            goto begin_return;
        }
        break;

    case 6:
        elly_scythe_speed -= 4;
        elly_scythe_angle += elly_scythe_turn;
        if(elly_scythe_speed > 4) {
            goto after_switch;
        }

    begin_return:
        elly_scythe_mode = 7;
        goto after_switch;

    case 7:
        elly_scythe_angle = iatan2(
            (boss.pos.cur.y.v - elly_scythe_motion.cur.y.v),
            (boss.pos.cur.x.v - elly_scythe_motion.cur.x.v)
        );
        elly_scythe_speed += 8;
        if((boss.pos.cur.x.v - TO_SP(16)) >= elly_scythe_motion.cur.x.v) {
            goto after_switch;
        }
        if((boss.pos.cur.x.v + TO_SP(16)) <= elly_scythe_motion.cur.x.v) {
            goto after_switch;
        }
        if((boss.pos.cur.y.v - TO_SP(16)) >= elly_scythe_motion.cur.y.v) {
            goto after_switch;
        }
        if((boss.pos.cur.y.v + TO_SP(16)) <= elly_scythe_motion.cur.y.v) {
            goto after_switch;
        }
        elly_scythe_mode = 8;
        elly_scythe_flag = 2;
        elly_scythe_frame = 0;
        goto after_switch;

    case 8:
        if((elly_scythe_frame < 32) && ((elly_scythe_frame & 7) == 0)) {
            boss.sprite = (((31 - elly_scythe_frame) >> 2) + 134);
        }
        if(elly_scythe_frame >= 32) {
            boss.sprite = 134;
            elly_scythe_mode = 0;
        }
    advance_frame:
        elly_scythe_frame++;
        break;
    }

    after_switch:
    if(elly_scythe_flag != 1) {
        return;
    }

    vector2(
        elly_scythe_motion.velocity.x.v,
        elly_scythe_motion.velocity.y.v,
        elly_scythe_angle,
        elly_scythe_speed
    );
    shot_hitbox_radius.x.v = TO_SP(32);
    shot_hitbox_radius.y.v = TO_SP(32);
    shot_hitbox_center.x.v = elly_scythe_motion.cur.x.v;
    shot_hitbox_center.y.v = elly_scythe_motion.cur.y.v;
    elly_scythe_motion.velocity.y.v -= (
        static_cast<unsigned int>(shots_hittest()) >> 1
    );
    elly_scythe_motion.update_seg3();

    if(
        ((elly_scythe_motion.cur.x.v - TO_SP(24)) < player_pos.cur.x.v) &&
        ((elly_scythe_motion.cur.x.v + TO_SP(24)) > player_pos.cur.x.v) &&
        ((elly_scythe_motion.cur.y.v - TO_SP(24)) < player_pos.cur.y.v) &&
        ((elly_scythe_motion.cur.y.v + TO_SP(24)) > player_pos.cur.y.v)
    ) {
        player_is_hit = true;
    }
}

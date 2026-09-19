#pragma option -zCB4M_UPDATE_TEXT -zPmain_03

#include <dos.h>
#include "th04/formats/std.hpp"
#include "th04/main/enemy/enemy.hpp"
#include "th04/main/playperf.hpp"
#include "th04/main/rank.hpp"
#include "th04/main/scroll.hpp"
#include "th04/main/tile/tile.hpp"
#include "th04/snd/snd.h"
#include "compat/rec98/libs/master.lib/master.hpp"
#include "compat/rec98/th03/math/randring.hpp"

extern "C" unsigned char near enemy_pos_update(void);
extern "C" void near enemy_velocity_set(void);
extern "C" void near enemy_aim_at_player(void);

#define SCRIPT_WORD(off) (*reinterpret_cast<unsigned short __es *>(&(instr[off])))

extern "C" unsigned char near enemy_script_update(void)
{
    register enemy_t near *enemy = enemy_cur;
    unsigned char duration;
    unsigned char advance;
    volatile int temp;

    _ES = FP_SEG(std_seg);

refetch:
    register unsigned char __es *instr =
        reinterpret_cast<unsigned char __es *>(enemy->script);
    instr += enemy->script_ip;

dispatch:
    // This case order preserves TC4J's target-observed physical basic-block order.
    switch(*instr) {
    case 0x01:
        if(enemy->cur_instr_frame == 0) {
            enemy->speed.v = instr[2];
            enemy->angle = instr[1];
            enemy_velocity_set();
        }
        if(enemy_pos_update()) goto killed;
        duration = instr[3];
        advance = 4;
        goto timed;

    case 0x02:
        if(enemy->cur_instr_frame == 0) enemy_velocity_set();
        if(enemy_pos_update()) goto killed;
        duration = instr[1];
        advance = 2;
        goto timed;

    case 0x03:
        if(enemy->cur_instr_frame == 0) {
            enemy->speed.v = instr[1];
            enemy_velocity_set();
        }
        if(enemy_pos_update()) goto killed;
        duration = instr[2];
        advance = 3;
        goto timed;

    case 0x04:
    case 0x05:
        if(enemy->cur_instr_frame == 0) {
            enemy->angle = instr[1];
            enemy->angle_delta = instr[3];
            enemy->speed.v = instr[2];
        }
        enemy_velocity_set();
        if(*instr == 0x05) {
            enemy->pos.velocity.x.v += static_cast<signed char>(instr[4]);
            enemy->pos.velocity.y.v += static_cast<signed char>(instr[5]);
            duration = instr[6];
            advance = 7;
        } else {
            duration = instr[4];
            advance = 5;
        }
        if(enemy_pos_update()) goto killed;
        enemy->angle += enemy->angle_delta;
        goto timed;

    case 0x0D:
    case 0x0E:
        enemy_velocity_set();
        if(*instr == 0x0E) {
            enemy->pos.velocity.x.v += static_cast<signed char>(instr[1]);
            enemy->pos.velocity.y.v += static_cast<signed char>(instr[2]);
            duration = instr[3];
            advance = 4;
        } else {
            duration = instr[1];
            advance = 2;
        }
        if(enemy_pos_update()) goto killed;
        enemy->angle += enemy->angle_delta;
        goto timed;

    case 0x06:
        if(enemy->cur_instr_frame == 0) enemy->pos.prev = enemy->pos.cur;
        duration = instr[1];
        advance = 2;
        goto timed;

    case 0x0B:
        if(enemy->cur_instr_frame == 0) enemy->pos.velocity.x.v = 0;
        enemy->pos.velocity.y.v = scroll_last_delta.v;
        if(enemy_pos_update()) goto killed;
        duration = instr[1];
        advance = 2;
        goto timed;

    case 0x07:
    case 0x08:
        if(enemy->cur_instr_frame == 0) {
            enemy->angle = 0;
            enemy->angle_delta = instr[2];
        }
        enemy->pos.velocity.x.v = static_cast<subpixel_t>(
            (static_cast<long>(instr[1]) * CosTable8[enemy->angle]) >> 8
        );
        enemy->pos.velocity.y.v = static_cast<signed char>(instr[3]);
        if(*instr == 0x08) {
            temp = enemy->pos.velocity.x.v;
            enemy->pos.velocity.x.v = enemy->pos.velocity.y.v;
            enemy->pos.velocity.y.v = temp;
        }
        if(enemy_pos_update()) goto killed;
        enemy->angle += enemy->angle_delta;
        duration = instr[4];
        advance = 5;
        goto timed;

    case 0x09:
        enemy->angle = instr[1];
        enemy->speed.v = instr[2];
        enemy_aim_at_player();
        goto advance_three;

    case 0x0A:
        enemy->angle += instr[1];
        enemy_velocity_set();
        goto advance_two;

    case 0x0C:
        enemy->speed.v += static_cast<signed char>(instr[1]);
        enemy_velocity_set();
        goto advance_two;

    case 0x11:
        enemy->angle = randring2_next16();
        goto advance_one;

    case 0x20:
        bullet_template.spawn_type = enemy->bullet_template.spawn_type;
        bullet_template.patnum = enemy->bullet_template.patnum;
        bullet_template.origin.x.v = (
            enemy->bullet_template.origin.x.v + enemy->pos.cur.x.v
        );
        bullet_template.origin.y.v = (
            enemy->bullet_template.origin.y.v + enemy->pos.cur.y.v
        );
        bullet_template.group = enemy->bullet_template.group;
        bullet_template.angle = enemy->bullet_template.angle;
        bullet_template.speed.v = enemy->bullet_template.speed.v;
        bullet_template.count = enemy->bullet_template.count;
        bullet_template.delta = enemy->bullet_template.delta;
        bullet_template_tune();
        bullets_add_regular();
        goto advance_one;

    case 0x21:
        enemy->autofire = false;
        enemy->bullet_template.spawn_type = instr[1];
        enemy->bullet_template.origin.x.v = SCRIPT_WORD(2);
        enemy->bullet_template.origin.y.v = SCRIPT_WORD(4);
        enemy->bullet_template.group = static_cast<bullet_group_t>(instr[6]);
        enemy->bullet_template.angle = instr[7];
        enemy->bullet_template.speed.v = instr[8];
        enemy->bullet_template.patnum = instr[9];
        enemy->bullet_template.count = instr[10];
        advance = 11;
        goto next;

    case 0x22:
        enemy->bullet_template.spawn_type = instr[1];
        goto advance_two;

    case 0x23:
        if(enemy->cur_instr_frame == 0) enemy->pos.prev = enemy->pos.cur;
        enemy->bullet_template.origin.x.v = SCRIPT_WORD(1);
        enemy->bullet_template.origin.y.v = SCRIPT_WORD(3);
        advance = 5;
        goto next;

    case 0x24:
        enemy->bullet_template.angle = instr[1];
        goto advance_two;

    case 0x25:
        enemy->bullet_template.angle += instr[1];
        goto advance_two;

    case 0x2D:
        enemy->bullet_template.angle = randring2_next16();
        goto advance_one;

advance_one:
    advance = 1;
    goto next;

    case 0x2A:
        enemy->bullet_template.patnum = instr[1];
        goto advance_two;

    case 0x29:
        enemy->bullet_template.count = instr[1];
        goto advance_two;

    case 0x26:
        enemy->bullet_template.speed.v = instr[1];
        goto advance_two;

    case 0x27:
        enemy->bullet_template.speed.v += instr[1];
        goto advance_two;

    case 0x28:
        enemy->bullet_template.group = static_cast<bullet_group_t>(instr[1]);
        goto advance_two;

    case 0x2C:
        temp = instr[1];
        if(playperf > 16) {
            temp = ((playperf - 16) * temp);
            temp = (temp / 32);
            temp = (instr[1] - temp);
            if(temp < 16) temp = 16;
        } else if(playperf < 16) {
            temp = ((16 - playperf) * temp);
            temp = (temp / 32);
            temp = (instr[1] + temp);
            if(temp >= 256) temp = 255;
        }
        if(rank == RANK_EASY) temp = 255;
        enemy->autofire_interval = static_cast<unsigned char>(temp);
        goto advance_two;

    case 0x2B:
        enemy->autofire = true;
        goto advance_one;

    case 0x2E:
        enemy->autofire = false;
        goto advance_one;

    case 0x30:
        enemy->bullet_template.delta.spread_angle = instr[1];
        goto advance_two;

    case 0x00:
    killed:
        enemy->flag = EF_KILLED;
        return 1;

    case 0x10:
        enemy->flag = EF_ALIVE;
        enemy->patnum_base = instr[1];
        enemy->hp = SCRIPT_WORD(2);
        enemy->score = SCRIPT_WORD(4);
        enemy->can_be_damaged = true;
        enemy->kills_player_on_collision = true;
        advance = 6;
        goto next;

    case 0x82:
        enemy->clip_x = true;
        goto advance_one;

    case 0x84:
        enemy->clip_x = true;
        enemy->clip_y = true;
        goto advance_one;

    case 0x83:
        enemy->clip_y = true;
        goto advance_one;

    case 0x85:
        enemy->anim_cels = instr[1];
        enemy->anim_frames_per_cel = instr[2];
        goto advance_three;

    case 0x86:
        snd_se_play(instr[1]);
        goto advance_two;

    case 0x87:
        enemy->patnum_base = instr[1];
        goto advance_two;

    case 0x88:
        enemy->can_be_damaged = false;
        advance = 1;
        enemy->autofire = false;
        goto next;

    case 0x89:
        enemy->can_be_damaged = true;
        advance = 1;
        enemy->autofire = (rank == RANK_LUNATIC);
        goto next;

    case 0x8C:
        enemy->kills_player_on_collision = false;
        goto advance_one;

    case 0x8D:
        enemy->kills_player_on_collision = true;
        goto advance_one;

    case 0x8A:
        enemy->pos.prev = enemy->pos.cur;
        enemy->pos.cur.x.v = SCRIPT_WORD(1);
        enemy->pos.cur.y.v = SCRIPT_WORD(3);
        advance = 5;
        duration = 0;
        goto timed;

    case 0x8B:
        enemy->pos.prev = enemy->pos.cur;
        enemy->pos.cur.x.v += static_cast<int>(SCRIPT_WORD(1));
        enemy->pos.cur.y.v += static_cast<int>(SCRIPT_WORD(3));
        advance = 5;
        duration = 0;
        goto timed;

    case 0x8E:
        enemy->patnum_base += instr[1];
        goto advance_two;

    case 0x12:
        enemy->angle = instr[1];
        enemy->speed.v = instr[2];
        enemy_velocity_set();
        goto advance_three;

advance_three:
    advance = 3;
    goto next;

    case 0x13:
        enemy->angle = instr[1];
        enemy->speed.v = instr[2];
        if(!enemy->spawned_in_left_half) enemy->angle = 0x80 - enemy->angle;
        enemy_velocity_set();
        goto advance_three;

    case 0x14:
        enemy->speed.v = instr[1];
        enemy_velocity_set();
        goto advance_two;

    case 0x8F:
        tile_ring_set_vo(
            enemy->pos.cur.x.v, enemy->pos.cur.y.v, instr[1]
        );
        goto advance_two;

advance_two:
    advance = 2;
    goto next;

    case 0x80:
    case 0x81:
        if(enemy->loop_i >= instr[2]) {
            enemy->loop_i = 0;
            goto advance_three;
        }
        enemy->loop_i++;
        if(*instr == 0x80) enemy->script_ip = instr[1];
        else enemy->script_ip -= instr[1];
        goto refetch;

    default:
        // The target reaches the frame branch with uninitialized locals.
        goto timed;
    }

timed:
    if(enemy->cur_instr_frame >= duration) {
        enemy->cur_instr_frame = 0;
        enemy->script_ip += advance;
    } else {
        enemy->cur_instr_frame++;
    }
    return 0;

next:
    enemy->script_ip += advance;
    instr += advance;
    goto dispatch;

}

#undef SCRIPT_WORD

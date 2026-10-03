#pragma option -zCB4M_UPDATE_TEXT -zPmain_03

#include <dos.h>
#include "th04/formats/std.hpp"
#include "th04/main/enemy/enemy.hpp"
#include "th04/main/playperf.hpp"
#include "th04/main/rank.hpp"
#include "th04/main/scroll.hpp"
#include "th04/main/tile/tile.hpp"
#include "th04/snd/snd.h"
#include "src/shared/runtime/api.hpp"
#include "src/main/math/randring.hpp"

extern "C" unsigned char near enemy_pos_update(void);
extern "C" void near enemy_velocity_set(void);
extern "C" void near enemy_aim_at_player(void);

// Enemy scripts live in the loaded STD resource, addressed through ES. Multi-
// byte operands use the PC-98's native little-endian word layout and need not
// be aligned. Keep this as a direct __es load: copying bytes into a host-sized
// integer would change both TC4J code generation and the future port contract.
#define SCRIPT_U16_AT(byte_offset) \
    (*reinterpret_cast<unsigned short __es *>(&(instruction[byte_offset])))

// The opcode values are part of the on-disk STD format. Macros deliberately
// retain literal integer types; TC4J can emit a different switch when these
// are expressed as an enum. The declaration order below is semantic only.
#define ESOP_KILL                           0x00
#define ESOP_MOVE_SET_ANGLE_SPEED           0x01
#define ESOP_MOVE_CURRENT_VELOCITY          0x02
#define ESOP_MOVE_SET_SPEED                 0x03
#define ESOP_MOVE_TURN                      0x04
#define ESOP_MOVE_TURN_WITH_ACCELERATION    0x05
#define ESOP_WAIT                           0x06
#define ESOP_MOVE_COSINE_X                  0x07
#define ESOP_MOVE_COSINE_Y                  0x08
#define ESOP_AIM_AT_PLAYER                  0x09
#define ESOP_ADD_MOVE_ANGLE                 0x0A
#define ESOP_MOVE_WITH_SCROLL               0x0B
#define ESOP_ADD_MOVE_SPEED                 0x0C
#define ESOP_MOVE_TURN_CURRENT              0x0D
#define ESOP_MOVE_TURN_ACCEL_CURRENT        0x0E
#define ESOP_ACTIVATE                       0x10
#define ESOP_RANDOMIZE_MOVE_ANGLE           0x11
#define ESOP_SET_MOVE_ANGLE_SPEED           0x12
#define ESOP_SET_MIRRORED_ANGLE_SPEED       0x13
#define ESOP_SET_MOVE_SPEED                 0x14
#define ESOP_FIRE                           0x20
#define ESOP_SET_BULLET_TEMPLATE            0x21
#define ESOP_SET_BULLET_SPAWN_TYPE          0x22
#define ESOP_SET_BULLET_OFFSET              0x23
#define ESOP_SET_BULLET_ANGLE               0x24
#define ESOP_ADD_BULLET_ANGLE               0x25
#define ESOP_SET_BULLET_SPEED               0x26
#define ESOP_ADD_BULLET_SPEED               0x27
#define ESOP_SET_BULLET_GROUP               0x28
#define ESOP_SET_BULLET_COUNT               0x29
#define ESOP_SET_BULLET_SPRITE              0x2A
#define ESOP_AUTOFIRE_ON                    0x2B
#define ESOP_SET_AUTOFIRE_INTERVAL          0x2C
#define ESOP_RANDOMIZE_BULLET_ANGLE         0x2D
#define ESOP_AUTOFIRE_OFF                   0x2E
#define ESOP_SET_BULLET_SPREAD_ANGLE        0x30
#define ESOP_LOOP_TO_OFFSET                 0x80
#define ESOP_LOOP_BACK                      0x81
#define ESOP_ENABLE_X_CLIP                  0x82
#define ESOP_ENABLE_Y_CLIP                  0x83
#define ESOP_ENABLE_XY_CLIP                 0x84
#define ESOP_SET_ANIMATION                  0x85
#define ESOP_PLAY_SOUND_EFFECT              0x86
#define ESOP_SET_SPRITE                     0x87
#define ESOP_DISABLE_DAMAGE_AND_AUTOFIRE    0x88
#define ESOP_ENABLE_DAMAGE_LUNATIC_AUTOFIRE 0x89
#define ESOP_SET_POSITION                   0x8A
#define ESOP_ADD_POSITION                   0x8B
#define ESOP_DISABLE_PLAYER_COLLISION       0x8C
#define ESOP_ENABLE_PLAYER_COLLISION        0x8D
#define ESOP_ADD_SPRITE                     0x8E
#define ESOP_SET_TILE_RING                  0x8F

extern "C" unsigned char near enemy_script_update(void)
{
    register enemy_t near *current_enemy = enemy_cur;
    unsigned char duration_frames;
    unsigned char instruction_size;
    volatile int scratch;

    _ES = FP_SEG(std_seg);

refetch_instruction:
    // [script] is the start of this enemy's bytecode and [script_ip] is its
    // byte offset. Loops change script_ip directly, so they must rebuild the
    // ES pointer instead of continuing from the current DI value.
    register unsigned char __es *instruction =
        reinterpret_cast<unsigned char __es *>(current_enemy->script);
    instruction += current_enemy->script_ip;

dispatch_opcode:
    // This case order preserves TC4J's target-observed physical basic-block order.
    switch(*instruction) {

    // Timed movement opcodes update position before testing their duration.
    // A duration of N therefore executes N+1 updates, including the update on
    // the frame where cur_instr_frame reaches N.
    case ESOP_MOVE_SET_ANGLE_SPEED:
        if(current_enemy->cur_instr_frame == 0) {
            current_enemy->speed.v = instruction[2];
            current_enemy->angle = instruction[1];
            enemy_velocity_set();
        }
        if(enemy_pos_update()) goto kill_enemy;
        duration_frames = instruction[3];
        instruction_size = 4;
        goto finish_timed_instruction;

    case ESOP_MOVE_CURRENT_VELOCITY:
        if(current_enemy->cur_instr_frame == 0) enemy_velocity_set();
        if(enemy_pos_update()) goto kill_enemy;
        duration_frames = instruction[1];
        instruction_size = 2;
        goto finish_timed_instruction;

    case ESOP_MOVE_SET_SPEED:
        if(current_enemy->cur_instr_frame == 0) {
            current_enemy->speed.v = instruction[1];
            enemy_velocity_set();
        }
        if(enemy_pos_update()) goto kill_enemy;
        duration_frames = instruction[2];
        instruction_size = 3;
        goto finish_timed_instruction;

    case ESOP_MOVE_TURN:
    case ESOP_MOVE_TURN_WITH_ACCELERATION:
        if(current_enemy->cur_instr_frame == 0) {
            current_enemy->angle = instruction[1];
            current_enemy->angle_delta = instruction[3];
            current_enemy->speed.v = instruction[2];
        }
        enemy_velocity_set();
        if(*instruction == ESOP_MOVE_TURN_WITH_ACCELERATION) {
            current_enemy->pos.velocity.x.v += static_cast<signed char>(instruction[4]);
            current_enemy->pos.velocity.y.v += static_cast<signed char>(instruction[5]);
            duration_frames = instruction[6];
            instruction_size = 7;
        } else {
            duration_frames = instruction[4];
            instruction_size = 5;
        }
        if(enemy_pos_update()) goto kill_enemy;
        current_enemy->angle += current_enemy->angle_delta;
        goto finish_timed_instruction;

    case ESOP_MOVE_TURN_CURRENT:
    case ESOP_MOVE_TURN_ACCEL_CURRENT:
        enemy_velocity_set();
        if(*instruction == ESOP_MOVE_TURN_ACCEL_CURRENT) {
            current_enemy->pos.velocity.x.v += static_cast<signed char>(instruction[1]);
            current_enemy->pos.velocity.y.v += static_cast<signed char>(instruction[2]);
            duration_frames = instruction[3];
            instruction_size = 4;
        } else {
            duration_frames = instruction[1];
            instruction_size = 2;
        }
        if(enemy_pos_update()) goto kill_enemy;
        current_enemy->angle += current_enemy->angle_delta;
        goto finish_timed_instruction;

    case ESOP_WAIT:
        if(current_enemy->cur_instr_frame == 0) current_enemy->pos.prev = current_enemy->pos.cur;
        duration_frames = instruction[1];
        instruction_size = 2;
        goto finish_timed_instruction;

    case ESOP_MOVE_WITH_SCROLL:
        if(current_enemy->cur_instr_frame == 0) current_enemy->pos.velocity.x.v = 0;
        current_enemy->pos.velocity.y.v = scroll_last_delta.v;
        if(enemy_pos_update()) goto kill_enemy;
        duration_frames = instruction[1];
        instruction_size = 2;
        goto finish_timed_instruction;

    case ESOP_MOVE_COSINE_X:
    case ESOP_MOVE_COSINE_Y:
        if(current_enemy->cur_instr_frame == 0) {
            current_enemy->angle = 0;
            current_enemy->angle_delta = instruction[2];
        }
        current_enemy->pos.velocity.x.v = static_cast<subpixel_t>(
            (static_cast<long>(instruction[1]) * CosTable8[current_enemy->angle]) >> 8
        );
        current_enemy->pos.velocity.y.v = static_cast<signed char>(instruction[3]);
        if(*instruction == ESOP_MOVE_COSINE_Y) {
            scratch = current_enemy->pos.velocity.x.v;
            current_enemy->pos.velocity.x.v = current_enemy->pos.velocity.y.v;
            current_enemy->pos.velocity.y.v = scratch;
        }
        if(enemy_pos_update()) goto kill_enemy;
        current_enemy->angle += current_enemy->angle_delta;
        duration_frames = instruction[4];
        instruction_size = 5;
        goto finish_timed_instruction;

    case ESOP_AIM_AT_PLAYER:
        current_enemy->angle = instruction[1];
        current_enemy->speed.v = instruction[2];
        enemy_aim_at_player();
        goto advance_three;

    case ESOP_ADD_MOVE_ANGLE:
        current_enemy->angle += instruction[1];
        enemy_velocity_set();
        goto advance_two;

    case ESOP_ADD_MOVE_SPEED:
        current_enemy->speed.v += static_cast<signed char>(instruction[1]);
        enemy_velocity_set();
        goto advance_two;

    case ESOP_RANDOMIZE_MOVE_ANGLE:
        current_enemy->angle = randring2_next16();
        goto advance_one;

    // FIRE copies the per-enemy template into the shared spawn scratch object.
    // Its stored origin is relative to the enemy's current position. Setup
    // opcodes below are immediate and may chain to another opcode this frame.
    case ESOP_FIRE:
        bullet_template.spawn_type = current_enemy->bullet_template.spawn_type;
        bullet_template.patnum = current_enemy->bullet_template.patnum;
        bullet_template.origin.x.v = (
            current_enemy->bullet_template.origin.x.v + current_enemy->pos.cur.x.v
        );
        bullet_template.origin.y.v = (
            current_enemy->bullet_template.origin.y.v + current_enemy->pos.cur.y.v
        );
        bullet_template.group = current_enemy->bullet_template.group;
        bullet_template.angle = current_enemy->bullet_template.angle;
        bullet_template.speed.v = current_enemy->bullet_template.speed.v;
        bullet_template.count = current_enemy->bullet_template.count;
        bullet_template.delta = current_enemy->bullet_template.delta;
        // Handwritten ABI preservation. The following indirect calls return
        // to a dispatcher whose instruction pointer remains in ES:DI.
        asm { push es; }
        bullet_template_tune();
        bullets_add_regular();
        asm { pop es; }
        goto advance_one;

    case ESOP_SET_BULLET_TEMPLATE:
        current_enemy->autofire = false;
        current_enemy->bullet_template.spawn_type = instruction[1];
        current_enemy->bullet_template.origin.x.v = SCRIPT_U16_AT(2);
        current_enemy->bullet_template.origin.y.v = SCRIPT_U16_AT(4);
        current_enemy->bullet_template.group = static_cast<bullet_group_t>(instruction[6]);
        current_enemy->bullet_template.angle = instruction[7];
        current_enemy->bullet_template.speed.v = instruction[8];
        current_enemy->bullet_template.patnum = instruction[9];
        current_enemy->bullet_template.count = instruction[10];
        instruction_size = 11;
        goto continue_immediately;

    case ESOP_SET_BULLET_SPAWN_TYPE:
        current_enemy->bullet_template.spawn_type = instruction[1];
        goto advance_two;

    case ESOP_SET_BULLET_OFFSET:
        if(current_enemy->cur_instr_frame == 0) current_enemy->pos.prev = current_enemy->pos.cur;
        current_enemy->bullet_template.origin.x.v = SCRIPT_U16_AT(1);
        current_enemy->bullet_template.origin.y.v = SCRIPT_U16_AT(3);
        instruction_size = 5;
        goto continue_immediately;

    case ESOP_SET_BULLET_ANGLE:
        current_enemy->bullet_template.angle = instruction[1];
        goto advance_two;

    case ESOP_ADD_BULLET_ANGLE:
        current_enemy->bullet_template.angle += instruction[1];
        goto advance_two;

    case ESOP_RANDOMIZE_BULLET_ANGLE:
        current_enemy->bullet_template.angle = randring2_next16();
        goto advance_one;

advance_one:
    instruction_size = 1;
    goto continue_immediately;

    case ESOP_SET_BULLET_SPRITE:
        current_enemy->bullet_template.patnum = instruction[1];
        goto advance_two;

    case ESOP_SET_BULLET_COUNT:
        current_enemy->bullet_template.count = instruction[1];
        goto advance_two;

    case ESOP_SET_BULLET_SPEED:
        current_enemy->bullet_template.speed.v = instruction[1];
        goto advance_two;

    case ESOP_ADD_BULLET_SPEED:
        current_enemy->bullet_template.speed.v += instruction[1];
        goto advance_two;

    case ESOP_SET_BULLET_GROUP:
        current_enemy->bullet_template.group = static_cast<bullet_group_t>(instruction[1]);
        goto advance_two;

    case ESOP_SET_AUTOFIRE_INTERVAL:
        // 16 is the neutral performance level. Higher performance shortens
        // the delay (down to 16 frames); lower performance lengthens it (up
        // to 255). Easy rank always selects that longest 8-bit delay.
        scratch = instruction[1];
        if(playperf > 16) {
            scratch = ((playperf - 16) * scratch);
            scratch /= 32;
            scratch = (instruction[1] - scratch);
            if(scratch < 16) scratch = 16;
        } else if(playperf < 16) {
            scratch = ((16 - playperf) * scratch);
            scratch /= 32;
            scratch = (instruction[1] + scratch);
            if(scratch >= 256) scratch = 255;
        }
        if(rank == RANK_EASY) scratch = 255;
        current_enemy->autofire_interval = static_cast<unsigned char>(scratch);
        goto advance_two;

    case ESOP_AUTOFIRE_ON:
        current_enemy->autofire = true;
        goto advance_one;

    case ESOP_AUTOFIRE_OFF:
        current_enemy->autofire = false;
        goto advance_one;

    case ESOP_SET_BULLET_SPREAD_ANGLE:
        current_enemy->bullet_template.delta.spread_angle = instruction[1];
        goto advance_two;

    case ESOP_KILL:
    kill_enemy:
        current_enemy->flag = EF_KILLED;
        return 1;

    // Lifecycle and presentation opcodes are immediate. ACTIVATE consumes
    // little-endian HP and score words and then continues parsing this frame.
    case ESOP_ACTIVATE:
        current_enemy->flag = EF_ALIVE;
        current_enemy->patnum_base = instruction[1];
        current_enemy->hp = SCRIPT_U16_AT(2);
        current_enemy->score = SCRIPT_U16_AT(4);
        current_enemy->can_be_damaged = true;
        current_enemy->kills_player_on_collision = true;
        instruction_size = 6;
        goto continue_immediately;

    case ESOP_ENABLE_X_CLIP:
        current_enemy->clip_x = true;
        goto advance_one;

    case ESOP_ENABLE_XY_CLIP:
        current_enemy->clip_x = true;
        current_enemy->clip_y = true;
        goto advance_one;

    case ESOP_ENABLE_Y_CLIP:
        current_enemy->clip_y = true;
        goto advance_one;

    case ESOP_SET_ANIMATION:
        current_enemy->anim_cels = instruction[1];
        current_enemy->anim_frames_per_cel = instruction[2];
        goto advance_three;

    case ESOP_PLAY_SOUND_EFFECT:
        snd_se_play(instruction[1]);
        goto advance_two;

    case ESOP_SET_SPRITE:
        current_enemy->patnum_base = instruction[1];
        goto advance_two;

    case ESOP_DISABLE_DAMAGE_AND_AUTOFIRE:
        current_enemy->can_be_damaged = false;
        instruction_size = 1;
        current_enemy->autofire = false;
        goto continue_immediately;

    case ESOP_ENABLE_DAMAGE_LUNATIC_AUTOFIRE:
        current_enemy->can_be_damaged = true;
        instruction_size = 1;
        current_enemy->autofire = (rank == RANK_LUNATIC);
        goto continue_immediately;

    case ESOP_DISABLE_PLAYER_COLLISION:
        current_enemy->kills_player_on_collision = false;
        goto advance_one;

    case ESOP_ENABLE_PLAYER_COLLISION:
        current_enemy->kills_player_on_collision = true;
        goto advance_one;

    case ESOP_SET_POSITION:
        current_enemy->pos.prev = current_enemy->pos.cur;
        current_enemy->pos.cur.x.v = SCRIPT_U16_AT(1);
        current_enemy->pos.cur.y.v = SCRIPT_U16_AT(3);
        instruction_size = 5;
        duration_frames = 0;
        goto finish_timed_instruction;

    case ESOP_ADD_POSITION:
        current_enemy->pos.prev = current_enemy->pos.cur;
        // The stored words are reinterpreted through TC4J's 16-bit int for
        // signed relative movement. Preserve that conversion in a port.
        current_enemy->pos.cur.x.v += static_cast<int>(SCRIPT_U16_AT(1));
        current_enemy->pos.cur.y.v += static_cast<int>(SCRIPT_U16_AT(3));
        instruction_size = 5;
        duration_frames = 0;
        goto finish_timed_instruction;

    case ESOP_ADD_SPRITE:
        current_enemy->patnum_base += instruction[1];
        goto advance_two;

    case ESOP_SET_MOVE_ANGLE_SPEED:
        current_enemy->angle = instruction[1];
        current_enemy->speed.v = instruction[2];
        enemy_velocity_set();
        goto advance_three;

advance_three:
    instruction_size = 3;
    goto continue_immediately;

    case ESOP_SET_MIRRORED_ANGLE_SPEED:
        current_enemy->angle = instruction[1];
        current_enemy->speed.v = instruction[2];
        if(!current_enemy->spawned_in_left_half) current_enemy->angle = 0x80 - current_enemy->angle;
        enemy_velocity_set();
        goto advance_three;

    case ESOP_SET_MOVE_SPEED:
        current_enemy->speed.v = instruction[1];
        enemy_velocity_set();
        goto advance_two;

    case ESOP_SET_TILE_RING:
        tile_ring_set_vo(
            current_enemy->pos.cur.x.v, current_enemy->pos.cur.y.v, instruction[1]
        );
        goto advance_two;

advance_two:
    instruction_size = 2;
    goto continue_immediately;

    case ESOP_LOOP_TO_OFFSET:
    case ESOP_LOOP_BACK:
        // Both forms share one loop counter. 0x80 jumps to an absolute byte
        // offset within this script; 0x81 subtracts a byte distance. The
        // instruction falls through after the requested iterations.
        if(current_enemy->loop_i >= instruction[2]) {
            current_enemy->loop_i = 0;
            goto advance_three;
        }
        current_enemy->loop_i++;
        if(*instruction == ESOP_LOOP_TO_OFFSET) current_enemy->script_ip = instruction[1];
        else current_enemy->script_ip -= instruction[1];
        goto refetch_instruction;

    default:
        // The target reaches the frame branch with uninitialized locals.
        goto finish_timed_instruction;
    }

finish_timed_instruction:
    // Unknown opcodes deliberately arrive here with uninitialized locals, as
    // in the target. Valid game data never needs that undefined path.
    if(current_enemy->cur_instr_frame >= duration_frames) {
        current_enemy->cur_instr_frame = 0;
        current_enemy->script_ip += instruction_size;
    } else {
        current_enemy->cur_instr_frame++;
    }
    return 0;

continue_immediately:
    // Setup opcodes do not consume a gameplay frame. Keep interpreting until
    // a timed opcode returns or KILL removes the enemy.
    current_enemy->script_ip += instruction_size;
    instruction += instruction_size;
    goto dispatch_opcode;

}

#undef SCRIPT_U16_AT

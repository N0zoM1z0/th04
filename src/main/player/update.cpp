#pragma option -zCmain_0_TEXT -zPmain_01

#include "x86real.h"
#include "th04/main/player/player.hpp"
#include "th04/main/player/move.hpp"
#include "th04/main/quit.hpp"
#include "src/shared/config/resident.hpp"
#include "compat/rec98/th02/snd/snd.h"

static const unsigned char MISS_ANIM_FRAMES = 32;
static const unsigned char MISS_ANIM_FLASH_AT = 28;
static const unsigned char DEATHBOMB_WINDOW = 8;
static const unsigned char MISS_INVINCIBILITY_FRAMES = 192;
static const unsigned char MISS_EXPLOSION_ANGLE_VELOCITY = 8;
static const unsigned int MISS_EXPLOSION_RADIUS_VELOCITY = (7 * 16);
static const unsigned char PLAYER_RESPAWN_MOTION_FRAMES = 72;
static const unsigned char SHOT_CYCLE_FRAMES = 18;
static const unsigned int SHOT_LASER_COOLDOWN_FRAMES = 32;

extern unsigned char miss_time;
extern unsigned int miss_explosion_radius;
extern unsigned char miss_explosion_angle;
extern unsigned char dream_items_collected;
extern const unsigned int DREAM_SCORE_PER_ITEMS[8];
extern unsigned int dream_score;
extern unsigned char playperf;
extern unsigned char bullet_clear_time;
extern unsigned char shot_time;
extern unsigned int shot_laser_time;
extern unsigned int __cdecl PaletteTone;
extern bool palette_changed;
extern SPPoint player_option_pos_cur;
extern SPPoint player_option_pos_prev;
extern input_t player_input_prev;
extern unsigned char player_respawn_motion_time;
extern nearfunc_t_near playchar_shot_func;
extern nearfunc_t_near player_bomb_func;

extern "C" void pascal far items_miss_add(void);
extern "C" void pascal far hud_dream_put(void);
void far hud_lives_put(void);
void far hud_bombs_put(void);
void far shot_level_update(void);
extern "C" void pascal far playperf_lower(char delta);
unsigned char near gameover_run(void);

#pragma samecodeseg hud_dream_put
#pragma samecodeseg shot_level_update
#pragma samecodeseg playperf_lower
#pragma samecodeseg hud_lives_put
#pragma samecodeseg hud_bombs_put

static void near player_miss_update(void)
{
    unsigned char power_loss;

    miss_time--;
    if(miss_time > MISS_ANIM_FRAMES) {
        return;
    }
    if(miss_time == MISS_ANIM_FRAMES) {
        player_pos.velocity.x.v = 0;
        player_pos.velocity.y.v = 0;
        power_overflow = 0;
        miss_explosion_radius = 0;
        items_miss_add();

        power_loss = (power / 4);
        if(power_loss > 16) {
            power_loss = 16;
        }
        power -= power_loss;

        if(dream_items_collected != 0) {
            dream_items_collected--;
        }
        dream_score = DREAM_SCORE_PER_ITEMS[dream_items_collected];
        hud_dream_put();
        shot_level_update();
        snd_se_play(2);
        if(playperf >= 22) {
            playperf = 21;
        }
        playperf_lower(4);
        resident->miss_count++;
    }

    miss_explosion_radius += MISS_EXPLOSION_RADIUS_VELOCITY;
    // Preserve the byte-valued angle update as one explicit expression lifetime.
    _AL = miss_explosion_angle;
    _AL += MISS_EXPLOSION_ANGLE_VELOCITY;
    miss_explosion_angle = _AL;
    if(miss_time >= (MISS_ANIM_FRAMES - MISS_ANIM_FLASH_AT)) {
        return;
    }
    if(resident->rem_lives > 1) {
        // Each flash branch owns its store, matching the original control flow.
        if(miss_time & 1) {
            PaletteTone = 150;
        } else {
            PaletteTone = 100;
        }
        palette_changed = true;
    }
    if(miss_time != 0) {
        return;
    }

    player_pos.cur.x.v = (192 * 16);
    player_pos.prev.x.v = (192 * 16);
    player_pos.cur.y.v = (368 * 16);
    player_pos.prev.y.v = (368 * 16);
    player_pos.velocity.x.v = 0;
    player_pos.velocity.y.v = -32;

    if(resident->rem_lives > 1) {
        resident->rem_lives--;
        hud_lives_put();
        resident->rem_bombs = resident->credit_bombs;
        hud_bombs_put();
        bullet_clear_time = 32;
        return;
    }
    quit = static_cast<quit_t>(gameover_run());
}

void near player_update(void)
{
    bool retry;
    move_ret_t move_ret;
    register input_t input;

    if(player_invincibility_time != 0) {
        player_invincibility_time--;
    }
    if(player_is_hit) {
        if(player_invincibility_time != 0) {
            player_is_hit = false;
        } else {
            if(shot_laser_time > (SHOT_LASER_COOLDOWN_FRAMES + 1)) {
                shot_laser_time = (SHOT_LASER_COOLDOWN_FRAMES + 1);
            }
            miss_time = (MISS_ANIM_FRAMES + DEATHBOMB_WINDOW);
            player_is_hit = false;
            player_invincibility_time = MISS_INVINCIBILITY_FRAMES;
            player_respawn_motion_time = PLAYER_RESPAWN_MOTION_FRAMES;
            player_pos.velocity.x.v = 0;
            player_pos.velocity.y.v = 0;
        }
    }

    if(player_respawn_motion_time == 0) {
        player_pos.velocity.x.v = 0;
        player_pos.velocity.y.v = 0;
        input = (key_det & INPUT_MOVEMENT);
        retry = true;
        do {
            move_ret = player_move(input);
            if(
                (move_ret != MOVE_INVALID) ||
                !retry ||
                (player_input_prev == input)
            ) {
                break;
            }
            input &= ~player_input_prev;
            retry = false;
        } while(true);

        if(shiftkey) {
            player_pos.velocity.x.v /= 2;
            player_pos.velocity.y.v /= 2;
        }
        player_pos_update_and_clamp();
        if(retry) {
            player_input_prev = input;
        }

        if((key_det & INPUT_SHOT) && (shot_time <= 1)) {
            shot_time = SHOT_CYCLE_FRAMES;
            goto fire_shot;
        }
        if(shot_time != 0) {
            shot_time--;
            if(
                (shot_time == ((SHOT_CYCLE_FRAMES / 3) * 1)) ||
                (shot_time == ((SHOT_CYCLE_FRAMES / 3) * 2))
            ) {
                goto fire_shot;
            }
            goto after_shot;
        }
        goto after_shot;

    fire_shot:
        playchar_shot_func();
        snd_se_play(1);
    after_shot:
    } else {
        player_pos.update_seg1();
        player_respawn_motion_time--;
    }

    player_option_pos_prev = player_option_pos_cur;
    player_option_pos_cur = player_pos.cur;
    player_option_pos_cur.x.v -= player_pos.velocity.x.v;
    player_option_pos_cur.y.v -= player_pos.velocity.y.v;

    if(key_det & INPUT_BOMB) {
        player_bomb_func();
    }
    if(miss_time != 0) {
        player_miss_update();
    }
}

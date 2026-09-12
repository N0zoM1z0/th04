#ifndef TH04_MUGETSU_MAIN033_COMBINED
#pragma option -zCMAIN_033_TEXT -zPmain_03
#include "compat/rec98/libs/master.lib/master.hpp"
#include "compat/rec98/th02/v_colors.hpp"
#include "th04/sprites/main_pat.h"
#include "th04/main/frames.h"
#include "th04/main/boss/boss.hpp"
#include "th04/main/bullet/bullet.hpp"
#include "th04/main/player/player.hpp"
#include "th04/math/randring.hpp"
#include "th04/snd/snd.h"

#pragma option -a
#endif

extern unsigned char bullet_special_turns_max;
extern unsigned char (near *mugetsu_transition_func)(void);
extern SPPoint mugetsu_anchor;
extern "C" unsigned char near mugetsu_180BB(void);
extern "C" unsigned char near mugetsu_1812A(void);
extern "C" unsigned char near mugetsu_1821E(void);
extern "C" void near mugetsu_18314(void);
extern "C" void near mugetsu_1838A(void);

extern unsigned char mugetsu_phase2_mode;

extern "C" void near mugetsu_1845E(void)
{
    switch(mugetsu_transition_func()) {
    case 1:
        bullet_template.spawn_type = BST_BULLET16_CLOUD_BACKWARDS;
        bullet_template.patnum = PAT_BULLET16_N_BALL_BLUE;
        bullet_template.group = BG_RING;
        bullet_template.count = 40;
        bullet_template.speed.v = TO_SP(1);
        bullet_template.angle = randring2_next16();
        bullets_add_regular();
        snd_se_play(15);
        return;
    case 2:
        boss.phase_frame = 0;
        boss.mode = -1;
        return;
    }
}

extern "C" void near mugetsu_184AC(void)
{
    switch(mugetsu_transition_func()) {
    case 1:
        bullet_template.special_motion = BSM_DECELERATE_THEN_TURN;
        bullet_template.group = BG_SINGLE;
        bullet_special_turns_max = 1;
        return;
    case 2:
        if(stage_frame_mod2 == 0) return;
        bullet_template.spawn_type = BST_BULLET16;
        bullet_template.patnum = PAT_BULLET16_N_SMALL_BALL_YELLOW;
        bullet_template.speed.v = static_cast<unsigned char>(randring2_next16_and(0x3F) + TO_SP(1));
        randring2_next16_mod(TO_SP(64));
        _DX = boss.pos.cur.x.v;
        _DX += -TO_SP(32);
        _AX += _DX;
        bullet_template.origin.x.v = _AX;
        randring2_next16_mod(TO_SP(32));
        _DX = boss.pos.cur.y.v;
        _DX += -TO_SP(26);
        _AX += _DX;
        bullet_template.origin.y.v = _AX;
        bullet_template.angle = 0;
        bullet_template_special_angle.turn_by = 0x40;
        bullets_add_special();
        bullet_template.speed.v = static_cast<unsigned char>(randring2_next16_and(0x3F) + TO_SP(1));
        bullet_template.angle = 0x80;
        bullet_template_special_angle.turn_by = -0x40;
        bullets_add_special();
        snd_se_play(9);
        return;
    case 3:
        boss.phase_frame = 0;
        boss.mode = -1;
        return;
    }
}

extern "C" void near mugetsu_18556(void)
{
    switch(mugetsu_transition_func()) {
    case 1:
        bullet_template.group = BG_RING;
        bullet_template.count = 32;
        bullet_template_tune();
        return;
    case 2:
        if(stage_frame_mod8 != 0) return;
        bullet_template.spawn_type = randring2_next16_and(BST_PELLET);
        bullet_template.patnum = PAT_BULLET16_N_BALL_BLUE;
        bullet_template.speed.v = static_cast<unsigned char>(randring2_next16_and(0x3F) + TO_SP(1));
        randring2_next16_mod(TO_SP(64));
        _DX = boss.pos.cur.x.v;
        _DX += -TO_SP(32);
        _AX += _DX;
        bullet_template.origin.x.v = _AX;
        randring2_next16_mod(TO_SP(32));
        _DX = boss.pos.cur.y.v;
        _DX += -TO_SP(26);
        _AX += _DX;
        bullet_template.origin.y.v = _AX;
        bullet_template.angle = randring2_next16();
        bullets_add_regular();
        snd_se_play(3);
        return;
    case 3:
        boss.phase_frame = 0;
        boss.mode = -1;
        return;
    }
}

extern "C" void near mugetsu_185E4(void)
{
    if(stage_frame_mod8 != 0) return;
    bullet_template.angle = boss.angle;
    bullet_template.group = BG_RING;
    bullet_template.count = 16;
    bullet_template.speed.v = static_cast<unsigned char>((boss.phase_frame / 256) + TO_SP(2));
    bullets_add_regular();
    bullet_template.patnum = PAT_BULLET16_D_BLUE;
    bullet_template.spawn_type = BST_BULLET16;
    bullet_template.angle = static_cast<unsigned char>(-(bullet_template.angle) * 2);
    bullet_template.count = 4;
    bullet_template.speed.v += TO_SP(1);
    bullets_add_regular();
    if((boss.phase_frame % 1024) < 512) {
        boss.angle += 3;
    } else {
        boss.angle -= 3;
    }
}

extern "C" void near mugetsu_18655(void)
{
    if(stage_frame_mod8 != 0) return;
    bullet_template.group = BG_RING;
    bullet_template.count = 32;
    bullet_template.patnum = PAT_BULLET16_D_BLUE;
    bullet_template.spawn_type = BST_BULLET16;
    bullet_template.angle = randring2_next16();
    bullet_template.speed.v = TO_SP(7);
    bullets_add_regular();
}

void pascal near mugetsu_phase2_next(explosion_type_t explosion_type, int next_end_hp)
{
    boss_items_drop();
    boss_explode_small(explosion_type);
    boss.phase++;
    boss.phase_frame = 0;
    boss.mode = 0;
    boss.phase_state.patterns_seen = 0;
    boss.hp = boss.phase_end_hp;
    boss.phase_end_hp = next_end_hp;
    mugetsu_phase2_mode = 0;
}

extern unsigned char boss_bomb_invincibility_frames;
extern "C" bool near mugetsu_186B9(void)
{
    if(boss_bomb_invincibility_frames != 0) {
        boss_hittest_shots_damage(TO_SP(48), TO_SP(48), 10);
    } else if((boss.sprite <= 130) && (boss.sprite != 0)) {
        return boss_hittest_shots();
    }
    boss.phase_frame++;
    return false;
}

extern bool bombing;
extern int midboss_frames_until;
extern func_t_near stage_vm;
extern "C" void pascal far nullfunc_far(void);
extern nearfunc_t_near bg_render_bombing_func;
extern unsigned char tiles_bb_col;
extern bool palette_changed;
extern unsigned char bullet_clear_time;
extern unsigned char bullet_zap;
extern unsigned char player_invincibility_time;
extern unsigned int __cdecl PaletteTone;
extern SPPoint homing_target;
extern void pascal near hud_hp_update_and_render(int hp_cur, int hp_max);
extern void pascal near boss_explode_big(unsigned int type);

#pragma codeseg MAI_TEXT main_01
extern void pascal near mugetsu_gengetsu_bg_render(void);
#pragma codeseg

#ifndef TH04_MUGETSU_MAIN033_COMBINED
#pragma option -a
#endif
void pascal far mugetsu_update(void)
{
    unsigned char next_mode;

    if(bombing != 0) {
        boss_bomb_invincibility_frames = 0x20;
    }
    if(boss_bomb_invincibility_frames != 0) {
        boss_bomb_invincibility_frames--;
    }

    bullet_template.origin.x.v = boss.pos.cur.x.v;
    bullet_template.origin.y.v = (boss.pos.cur.y.v - TO_SP(10));
    bullet_template.spawn_type = BST_PELLET;

    switch(boss.phase) {
    case 0:
        if(boss.phase_frame == 0) {
            stage_vm = nullfunc_far;
            midboss_frames_until = 0;
            mugetsu_transition_func = mugetsu_180BB;
            boss_bomb_invincibility_frames = 0;
            boss.hp = 9400;
            boss.phase_end_hp = 3700;
            mugetsu_anchor.x.v = boss.pos.cur.x.v;
            mugetsu_anchor.y.v = boss.pos.cur.y.v;
        }
        mugetsu_186B9();
        if(boss.phase_frame <= 128) goto update_tail;
        boss.phase++;
        boss.phase_frame = 0;
        snd_se_play(13);
        tiles_bb_col = V_WHITE;
        bg_render_bombing_func = mugetsu_gengetsu_bg_render;
        goto update_tail;

    case 1:
        mugetsu_186B9();
        if(boss.phase_frame < 64) goto update_tail;
        boss.phase++;
        boss.mode = 0;
        boss.phase_state.patterns_seen = 2;
        boss.phase_frame = 0;
        boss.pos.velocity.x.v = 0;
        mugetsu_phase2_mode = 0;
        goto update_tail;

    case 2:
        switch(boss.mode) {
        case 0:
        case 6:
            goto mode_0_6;
        case 3:
            mugetsu_184AC();
            break;
        case 1:
        case 4:
        case 5:
            mugetsu_1845E();
            break;
mode_0_6:
            mugetsu_18314();
            break;
        case 2:
        case 7:
            mugetsu_1838A();
            break;
        case 0xFF:
            if(boss.phase_frame > 16) {
                if(randring2_next16_and(3) == 0) {
                    mugetsu_transition_func = mugetsu_180BB;
                } else {
                    mugetsu_transition_func = mugetsu_1812A;
                    do {
                        next_mode = randring2_next16_mod(5);
                        _AL = boss.phase_state.patterns_seen;
                    } while(_AL == next_mode);
                    _AL = next_mode;
                    boss.phase_state.patterns_seen = _AL;
                    _AH = 0;
                    _AX <<= 6;
                    _AX <<= 4;
                    _AX += TO_SP(64);
                    mugetsu_anchor.x.v = _AX;
                    mugetsu_anchor.y.v = boss.pos.cur.y.v;
                }
                boss.phase_frame = 0;
                mugetsu_phase2_mode++;
                boss.mode = (mugetsu_phase2_mode & 7);
            }
            break;
        }
        if((mugetsu_phase2_mode >= 32) && (boss.mode != 0xFF) && (boss.phase_frame > 24)) {
            mugetsu_18655();
        }
        if(mugetsu_phase2_mode < 36) {
            if(!mugetsu_186B9()) goto update_tail;
            boss_score_bonus(100);
        }
        if(bullet_clear_time < 20) {
            bullet_clear_time = 20;
        }
        mugetsu_phase2_next(ET_CIRCLE, 0);
        mugetsu_anchor.x.v = TO_SP(192);
        goto update_tail;

    case 3:
        mugetsu_186B9();
        if(boss.phase_frame < 64) goto update_tail;
        boss.phase++;
        mugetsu_transition_func = mugetsu_1821E;
        boss.phase_frame = 0;
        goto update_tail;

    case 4:
        mugetsu_186B9();
        mugetsu_18556();
        if(boss.phase_frame != 0) goto update_tail;
        boss_explode_small(ET_HORIZONTAL);
        boss.phase++;
        boss.phase_frame = 0;
        boss.sprite = 129;
        goto update_tail;

    case 5:
        mugetsu_186B9();
        if(boss.phase_frame < 128) goto update_tail;
        boss.phase++;
        boss.phase_frame = 0;
        goto update_tail;

    case 6:
        mugetsu_185E4();
        if(boss.phase_frame >= 3000) {
            mugetsu_18655();
        }
        if(!mugetsu_186B9() && (boss.phase_frame < 4000)) goto update_tail;
        boss_explode_small(ET_NW_SE);
        boss.phase++;
        if(boss.phase_frame < 4000) {
            boss.phase_state.patterns_seen = 1;
        } else {
            boss.phase_state.patterns_seen = 0;
        }
        boss.phase_frame = 0;
        boss.mode = 0;
        PaletteTone = 100;
        palette_changed = true;
        goto update_tail;

    case 7:
        boss.phase_frame++;
        if(boss.phase_frame == 16) {
            boss_explode_small(ET_VERTICAL);
        }
        if(boss.phase_frame == 32) {
            boss_explode_big(static_cast<unsigned int>(ET_SW_NE));
            boss.phase = PHASE_EXPLODE_BIG;
            bullet_zap = boss.phase_state.defeat_bonus;
            if(boss.phase_state.defeat_bonus != 0) {
                boss_score_bonus(200);
            }
            boss.sprite = PAT_ENEMY_KILL;
            boss.phase_frame = 0;
            snd_se_play(12);
            palette_changed = true;
            player_invincibility_time = BOSS_DEFEAT_INVINCIBILITY_FRAMES;
        }
        goto update_tail;

    default:
        boss_defeat_update();
        return;
    }

update_tail:
    homing_target.x.v = boss.pos.cur.x.v;
    homing_target.y.v = boss.pos.cur.y.v;
    hud_hp_update_and_render(boss.hp, 9400);
}

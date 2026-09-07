// TH04 Elly MAIN_034 physical producer recovered from target relocation/table layout.
#pragma option -zCMAIN_034_TEXT -zPmain_03
#define TH04_ELLY_MAIN034_COMBINED 1

#include "compat/rec98/libs/master.lib/master.hpp"
#include "compat/rec98/libs/master.lib/pc98_gfx.hpp"
#include "th04/snd/snd.h"
#include "th04/sprites/main_pat.h"
#include "th04/main/frames.h"
#include "th04/math/vector.hpp"
#include "compat/rec98/th03/math/polar.hpp"
#include "compat/rec98/th02/v_colors.hpp"
#include "compat/rec98/th03/math/randring.hpp"
#include "th04/main/gather.hpp"
#include "th04/main/circle.hpp"
#include "th04/main/spark.hpp"
#include "th04/main/boss/boss.hpp"
#include "th04/main/player/player.hpp"

#pragma option -a

#include "th04/ellyscy.cpp"
#include "th04/ellyini.cpp"
#include "th04/ellyorb.cpp"
#include "th04/ellyph1.cpp"
#include "th04/ellyph2.cpp"
#include "th04/ellygath.cpp"
#include "th04/ellybrst.cpp"
#include "th04/ellyswp.cpp"
#include "th04/ellyring.cpp"
#include "th04/ellycld.cpp"
#include "th04/ellydual.cpp"
#include "th04/ellycl2.cpp"
#include "th04/ellyr16.cpp"
#include "th04/elly4rng.cpp"
#include "th04/ellyfin.cpp"

#ifndef TH04_ELLY_MAIN034_COMBINED
#pragma option -zCMAIN_034_TEXT -zPmain_03

#include "compat/rec98/libs/master.lib/master.hpp"
#include "compat/rec98/libs/master.lib/pc98_gfx.hpp"
#include "th04/snd/snd.h"
#include "th04/sprites/main_pat.h"
#include "th04/main/frames.h"
#include "th04/main/spark.hpp"
#ifndef TH04_ELLY_MAIN034_COMBINED
#include "th04/main/bullet/bullet.hpp"
#endif
#include "th04/main/boss/boss.hpp"
#include "th04/main/player/player.hpp"

#pragma option -a

#endif

extern unsigned char elly_scythe_mode;
extern unsigned char elly_scythe_flag;
extern int elly_orbit_frame;
extern unsigned char elly_pattern_group;
extern nearfunc_t_near bg_render_bombing_func;
extern unsigned char tiles_bb_col;
#pragma codeseg MAI_TEXT main_01
extern void pascal near elly_bg_render(void);
#pragma codeseg
extern bool palette_changed;
extern unsigned char bullet_clear_time;
extern unsigned char bullet_zap;
extern unsigned char player_invincibility_time;
extern SPPoint homing_target;
extern void pascal near hud_hp_update_and_render(int hp_cur, int hp_max);
extern void pascal near boss_explode_big(unsigned int type);

extern "C" void near elly_scythe_update(void);
extern "C" void near elly_orbit_update(void);
extern "C" void near elly_phase_scythe(void);
extern "C" void near elly_phase_orbit(void);
extern "C" void near elly_phase_sweep(void);
extern "C" void near elly_phase_ring(void);
extern "C" void near elly_phase_cloud(void);
extern "C" void near elly_phase_dual(void);
extern "C" void near elly_phase_cloud_reverse(void);
extern "C" void near elly_phase_ring16(void);
extern "C" void near elly_phase_four_rings(void);
extern "C" void near elly_phase_final(void);

void pascal far elly_update(void)
{
    elly_scythe_update();

    switch(boss.phase) {
    case 0:
        elly_scythe_flag = 0;
        elly_scythe_mode = 0;
        boss.phase++;
        boss.mode = 0;
        Palettes[0].c.b = 128;
        palette_changed = true;
        boss.hp = 6000;
        boss.phase_end_hp = 6000;
        break;

    case 1:
        boss.pos.update_seg3();
        switch(boss.mode) {
        case 0:
            elly_phase_scythe();
            break;
        case 0xFF:
            if(boss.phase_frame <= 64) {
                if((boss.phase_state.patterns_seen == 0) ||
                   (boss.phase_state.patterns_seen == 3)) {
                    boss.pos.velocity.x.v = -TO_SP(1);
                } else if((boss.phase_state.patterns_seen == 1) ||
                          (boss.phase_state.patterns_seen == 2)) {
                    boss.pos.velocity.x.v = TO_SP(1);
                }
            } else {
                if(boss.phase_state.patterns_seen < 3) {
                    boss.phase_state.patterns_seen++;
                } else {
                    boss.phase_state.patterns_seen = 0;
                }
                boss.mode = 0;
                boss.phase_frame = 0;
                boss.pos.velocity.x.v = 0;
            }
            break;
        }
        boss.phase_frame++;
        boss_hittest_shots_invincible();
        if(stage_frame < 9240) {
            break;
        }
        boss.phase++;
        boss.phase_frame = 0;
        snd_se_play(13);
        boss.pos.velocity.y.v = 8;
        bg_render_bombing_func = elly_bg_render;
        tiles_bb_col = 0;
        break;

    case 2:
        boss.pos.update_seg3();
        if(boss.pos.cur.x.v < TO_SP(192)) {
            boss.pos.velocity.x.v = TO_SP(2);
        } else if(boss.pos.cur.x.v >= TO_SP(193)) {
            boss.pos.velocity.x.v = -TO_SP(2);
        } else {
            boss.pos.velocity.x.v = 0;
        }
        boss_hittest_shots_invincible();
        if(boss.phase_frame < 32) {
            break;
        }
        boss.pos.velocity.x.v = 0;
        Palettes[0].c.b = 0;
        palette_changed = true;
        elly_orbit_frame = 0;
        boss.pos.cur.x.v = TO_SP(192);
        boss.pos.cur.y.v = TO_SP(96);
        boss.pos.prev.x.v = 0;
        boss_phase_next(ET_NONE, 0);
        elly_pattern_group = 0;
        break;

    case 3:
        bullet_template.origin.x.v = boss.pos.cur.x.v;
        bullet_template.origin.y.v = boss.pos.cur.y.v;
        switch(boss.mode) {
        case 0:
            elly_phase_orbit();
            break;
        case 1:
            elly_phase_sweep();
            break;
        case 2:
            elly_phase_ring();
            break;
        case 3:
            elly_phase_cloud();
            break;
        case 4:
            elly_phase_dual();
            break;
        case 5:
            elly_phase_cloud_reverse();
            break;
        case 6:
            elly_phase_ring16();
            break;
        case 7:
            elly_phase_four_rings();
            break;
        case 8:
            elly_phase_final();
            break;
        case 0xFF:
            if(boss.phase_frame < 32) {
                elly_orbit_update();
                elly_orbit_frame++;
                break;
            }
            boss.phase_state.patterns_seen++;
            switch(elly_pattern_group) {
            case 0:
                boss.mode = (boss.phase_state.patterns_seen % 2);
                if(boss.phase_state.patterns_seen < 8) {
                    goto pattern_reset_frame;
                }
            pattern_group_done:
                boss_explode_small(
                    static_cast<explosion_type_t>(elly_pattern_group)
                );
                boss.mode = -1;
                elly_pattern_group++;
                boss.hp = (6000 - (elly_pattern_group * 1500));
                goto pattern_reset_frame;

            case 1:
                boss.mode = (boss.phase_state.patterns_seen % 4);
                if(boss.phase_state.patterns_seen >= 16) {
                    goto pattern_group_done;
                }
                break;

            case 2:
                boss.mode = ((boss.phase_state.patterns_seen % 4) + 2);
                if(boss.phase_state.patterns_seen >= 24) {
                    goto pattern_group_done;
                }
                break;

            case 3:
                boss.mode = ((boss.phase_state.patterns_seen % 4) + 4);
                if(boss.phase_state.patterns_seen >= 32) {
                    goto pattern_group_done;
                }
                break;

            case 4:
                boss.mode = ((boss.phase_state.patterns_seen % 4) + 5);
                if(boss.phase_state.patterns_seen < 40) {
                    goto pattern_reset_frame;
                }
                boss.phase_state.patterns_seen = 0;
                goto phase_complete;

            default:
                goto pattern_reset_frame;
            }

        pattern_reset_frame:
            boss.phase_frame = 0;
            break;
        }

        if(boss_hittest_shots()) {
            boss.phase_state.patterns_seen = 1;
        phase_complete:
            boss.phase++;
            sparks_add_circle(
                boss.pos.cur.x, boss.pos.cur.y, TO_SP(8), 48
            );
            boss_explode_small(ET_VERTICAL);
            boss.phase_frame = 0;
        }

        if(elly_pattern_group == 0) {
            if(boss.hp <= 4700) {
                goto phase_hp_done;
            }
        }
        if(elly_pattern_group == 1) {
            if(boss.hp <= 3300) {
                goto phase_hp_done;
            }
        }
        if(elly_pattern_group == 2) {
            if(boss.hp <= 2100) {
                goto phase_hp_done;
            }
        }
        if(elly_pattern_group == 3) {
            if(boss.hp <= 700) {
                goto phase_hp_done;
            }
        }
        break;

    phase_hp_done:
        boss_items_drop();
        if(bullet_clear_time < 20) {
            bullet_clear_time = 20;
        }
        boss_score_bonus(10);
        boss_explode_small(static_cast<explosion_type_t>(elly_pattern_group));
        boss.mode = -1;
        boss.phase_frame = 0;
        elly_pattern_group++;
        break;

    case 4:
        boss.phase_frame++;
        if(boss.phase_frame == 16) {
            boss_explode_small(ET_VERTICAL);
        }
        if(boss.phase_frame == 32) {
            boss_explode_big(static_cast<unsigned int>(ET_HORIZONTAL));
            boss.phase = PHASE_EXPLODE_BIG;
            bullet_zap = boss.phase_state.defeat_bonus;
            if(boss.phase_state.defeat_bonus != 0) {
                boss_score_bonus(40);
            }
            boss.sprite = PAT_ENEMY_KILL;
            boss.phase_frame = 0;
            snd_se_play(12);
            player_invincibility_time = BOSS_DEFEAT_INVINCIBILITY_FRAMES;
            elly_scythe_mode = 0;
            elly_scythe_flag = 0;
        }
        break;

    default:
        boss_defeat_update();
        return;
    }

    homing_target.x.v = boss.pos.cur.x.v;
    homing_target.y.v = boss.pos.cur.y.v;
    hud_hp_update_and_render(boss.hp, 6000);
}

#undef TH04_ELLY_MAIN034_COMBINED

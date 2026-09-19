#pragma option -zCDEMO_TEXT -zPmain_01

// Maintained natural source for the reviewed DEMO_TEXT gameplay-session initializer.
// Current production-profile TC4J omits one target compiler-metadata byte after RET.

#include "src/shared/runtime/api.hpp"
#include "compat/rec98/th01/rank.h"
#include "th04/end/end.h"
#include "th04/playchar.h"
#include "th04/resident.hpp"
#include "th04/sprites/main_pat.h"
#include "th04/main/stage/stage.hpp"
#include "th04/main/player/player.hpp"
#include "th04/main/player/bomb.hpp"
#include "th04/main/bullet/bullet.hpp"
#include "th04/main/playperf.hpp"
#include "th04/main/rank.hpp"
#include "th04/main/score.hpp"
#include "th04/main/slowdown.hpp"
#include "th04/main/hiscore.hpp"

extern unsigned char power;
extern unsigned int player_option_patnum;
extern nearfunc_t_near near *playchar_shot_funcs;
extern nearfunc_t_near near SHOT_FUNCS_REIMU_A[];
extern nearfunc_t_near near SHOT_FUNCS_REIMU_B[];
extern nearfunc_t_near near SHOT_FUNCS_MARISA_A[];
extern nearfunc_t_near near SHOT_FUNCS_MARISA_B[];

void pascal near bb_txt_load(void);
void near score_reset(void);

void near gameplay_session_init(void)
{
    resident->graze = 0;
    resident->miss_count = 0;
    resident->bombs_used = 0;
    resident->end_sequence = ES_INGAME;

    playchar = static_cast<playchar_t>(
        resident->playchar_ascii == ('0' + PLAYCHAR_MARISA)
    );

    for(int i = 0; i < SCORE_DIGITS; i++) {
        score.digits[i] = 0;
    }

    power = POWER_MIN;
    resident->rem_bombs = resident->credit_bombs;
    resident->rem_lives = resident->credit_lives;
    bb_txt_load();

    if(playchar == PLAYCHAR_REIMU) {
        player_option_patnum = PAT_OPTION_REIMU;
        if(resident->shottype == SHOTTYPE_A) {
            playchar_shot_funcs = SHOT_FUNCS_REIMU_A;
        } else {
            playchar_shot_funcs = SHOT_FUNCS_REIMU_B;
        }
        player_bomb_func = player_bomb;
        playchar_bomb_func = bomb_reimu;
    } else {
        player_option_patnum = PAT_OPTION_MARISA;
        if(resident->shottype == SHOTTYPE_A) {
            playchar_shot_funcs = SHOT_FUNCS_MARISA_A;
        } else {
            playchar_shot_funcs = SHOT_FUNCS_MARISA_B;
        }
        player_bomb_func = player_bomb;
        playchar_bomb_func = bomb_marisa;
    }

    if(resident->demo_num != 0) {
        playperf = 28;
        rank = RANK_HARD;
        turbo_mode = true;
    } else {
        playperf = 16;
        if(stage_id == 6) {
            rank = RANK_EXTRA;
            turbo_mode = true;
        } else {
            rank = resident->rank;
            turbo_mode = resident->turbo_mode;
        }
    }

    score_reset();
    hiscore_load();

    switch(rank) {
    case RANK_EASY:
        graze_score = 100;
        playperf_min = 4;
        playperf_max = 16;
        bullets_add_regular = bullets_add_regular_easy;
        bullets_add_special = bullets_add_special_easy;
        bullet_template_tune = bullet_template_tune_easy;
        break;

    case RANK_NORMAL:
        graze_score = 250;
        playperf_min = 11;
        playperf_max = 24;
        bullets_add_regular = bullets_add_regular_normal;
        bullets_add_special = bullets_add_special_normal;
        bullet_template_tune = bullet_template_tune_normal;
        break;

    case RANK_HARD:
        playperf = 20;
        graze_score = 400;
        playperf_min = 20;
        playperf_max = 32;
        bullets_add_regular = bullets_add_regular_hard_lunatic;
        bullets_add_special = bullets_add_special_hard_lunatic;
        bullet_template_tune = bullet_template_tune_hard;
        break;

    case RANK_LUNATIC:
        graze_score = 500;
        playperf = 22;
        playperf_min = 22;
        playperf_max = 34;
        bullets_add_regular = bullets_add_regular_hard_lunatic;
        bullets_add_special = bullets_add_special_hard_lunatic;
        bullet_template_tune = bullet_template_tune_lunatic;
        break;

    case RANK_EXTRA:
        graze_score = 2560;
        playperf_min = 16;
        playperf_max = 20;
        bullets_add_regular = bullets_add_regular_normal;
        bullets_add_special = bullets_add_special_normal;
        bullet_template_tune = bullet_template_tune_normal;
        break;
    }
}

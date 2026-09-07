#include "th04/main/frames.h"
#include "th04/main/null.hpp"
#include "th04/main/midboss/midboss.hpp"
#include "th04/main/hud/hud.hpp"
#include "th04/math/randring.hpp"
#include "th04/sprites/main_pat.h"
#include "th04/main/score.hpp"
#include "th04/main/pointnum/pointnum.hpp"
#include "th04/main/boss/boss.hpp"

void midboss_reset(void)
{
	midboss_invalidate = nullfunc_near;
	midboss_render = nullfunc_near;
	midboss_update = nullfunc_far;
#if (GAME == 4)
	midboss_active = false;
#endif
	midboss.hp = 0;
}

void midboss_activate_if_stage_frame_is_midboss_start_frame(void)
{
	if(midboss.frames_until == stage_frame) {
		midboss_invalidate = midboss_invalidate_func;
		midboss_render = midboss_render_func;
		midboss_update = midboss_update_func;
		midboss.phase = 0;
		midboss.phase_frame = 0;
		midboss_active = true;
	}
}

void pascal near hud_hp_update_and_render(int hp_cur, int hp_max)
{
	#define value_prev hud_hp_bar_value_prev
	extern int value_prev;

	int value_cur;

	if(hp_cur <= 0) {
		value_cur = 0;
	} else if(hp_cur >= hp_max) {
		value_cur = BAR_MAX;
	} else {
		value_cur = ((static_cast<long>(hp_cur) * BAR_MAX) / hp_max);
		if(value_cur < BAR_MAX) {
			value_cur++;
		}
	}
	if(value_prev < value_cur) {
		value_prev++;
	}
	if(value_prev > value_cur) {
		value_prev = value_cur;
	}
	hud_hp_put(value_prev);

	#undef value_prev
}

static const subpixel_t BONUS_AREA_W = TO_SP(PLAYFIELD_W / 3);
static const subpixel_t BONUS_AREA_H = TO_SP(PLAYFIELD_W / 3);

#define bonus_pointnum_add(base_left, base_top, points) { \
	subpixel_t center_x = (base_left + randring2_next16_mod(BONUS_AREA_W)); \
	if(center_x < to_sp(0.0f)) { \
		center_x = to_sp(0.0f); \
	} else if(center_x > to_sp(PLAYFIELD_W)) { \
		center_x = to_sp(PLAYFIELD_W); \
	} \
	pointnums_add_yellow( \
		center_x, (base_top + randring2_next16_mod(BONUS_AREA_H)), points \
	); \
}

#define score_bonus(units, value, center) { \
	score_delta += (units * value); \
	pointnum_times_2 = false; \
	subpixel_t base_left = (center.x.v - (BONUS_AREA_W / 2)); \
	subpixel_t base_top = (center.y.v - (BONUS_AREA_H / 2)); \
	for(unsigned int i = 0; i < units; i++) { \
		bonus_pointnum_add(base_left, base_top, value); \
	} \
}

void pascal near midboss_score_bonus(unsigned int units)
{
	score_bonus(units, MIDBOSS_BONUS_UNIT_VALUE, midboss.pos.cur);
}

// Probably only here because the code is identical to the midboss version.
void pascal near boss_score_bonus(unsigned int units)
{
	score_bonus(units, BOSS_BONUS_UNIT_VALUE, boss.pos.cur);
	boss_phase_timed_out = false;
}

void near midboss_defeat_update(void)
{
	if(midboss.phase == PHASE_EXPLODE_BIG) {
		if(midboss.phase_frame == 0) {
			playfield_shake_anim_time = 12;
		}

		midboss.phase_frame++;

		if((midboss.phase_frame % 16) == 0) {
			midboss.sprite++;
			if(midboss.sprite >= (PAT_ENEMY_KILL_last + 1)) {
				midboss.phase = PHASE_NONE;
			}
		}
	} else {
		midboss_reset();
	}
}

#pragma option -G

#include "compat/rec98/libs/master.lib/master.hpp"
#include "compat/rec98/th01/math/overlap.hpp"
#include "th04/math/vector.hpp"
#include "th04/main/frames.h"
#include "th04/main/scroll.hpp"
#include "th04/main/drawp.hpp"
#include "th04/main/playperf.hpp"
#include "th04/main/score.hpp"
#include "th04/main/slowdown.hpp"
#include "th04/main/bullet/pellet_r.hpp"
#include "th04/main/bullet/clearzap.hpp"
#include "th04/main/player/player.hpp"
#include "th04/main/spark.hpp"
#include "th04/main/hud/hud.hpp"
#include "th04/main/hud/overlay.hpp"
#include "th04/main/pointnum/pointnum.hpp"
#include "compat/rec98/th01/sprites/pellet.h"
#include "compat/rec98/th02/sprites/bullet16.h"

#if (GAME == 5)
#include "th04/main/item/item.hpp"
#include "compat/rec98/th05/sprites/main_pat.h"

static const int SLOWDOWN_BULLET_THRESHOLD_UNUSED = 32;

// Updates [bullet]'s patnum based on its current angle.
void pascal near bullet_update_patnum(bullet_t near &bullet)
{
	unsigned char patnum_base; // main_patnum_t, obviously

	if(bullet.patnum < PAT_BULLET16_D) {
		return;
	}
	if(bullet.patnum < (PAT_BULLET16_D_BLUE_last + 1)) {
		patnum_base = PAT_BULLET16_D_BLUE;
	} else if(bullet.patnum < (PAT_BULLET16_D_GREEN_last + 1)) {
		patnum_base = PAT_BULLET16_D_GREEN;
	} else if(bullet.patnum < (PAT_BULLET16_V_RED_last + 1)) {
		patnum_base = PAT_BULLET16_V_RED;
	} else {
		patnum_base = PAT_BULLET16_V_BLUE;
	}
	bullet.patnum = bullet_patnum_for_angle(patnum_base, bullet.angle);
}
#else
#include "th04/sprites/main_pat.h"

static const int SLOWDOWN_BULLET_THRESHOLD_UNUSED = 24;

inline void bullet_update_patnum(bullet_t near &bullet) {
}
#endif

#pragma option -a2

#define bullet_velocity_set_from_angle_and_speed(bullet) \
	vector2_near(bullet.pos.velocity, bullet.angle, bullet.speed_cur)

void pascal near bullet_turn_x(bullet_t near &bullet)
{
	bullet.u1.turns_done++;
	bullet.angle = (0x80 - bullet.angle);
	if(bullet.u1.turns_done >= bullet_special.turns_max) {
		bullet.move_flag = BMF_REGULAR;
	}
	bullet_velocity_set_from_angle_and_speed(bullet);
	bullet_update_patnum(bullet);
}

void pascal near bullet_turn_y(bullet_t near &bullet)
{
	bullet.u1.turns_done++;
	bullet.angle = (/* 0x00 */ - bullet.angle);
	if(bullet.u1.turns_done >= bullet_special.turns_max) {
		bullet.move_flag = BMF_REGULAR;
	}
	bullet_velocity_set_from_angle_and_speed(bullet);
	bullet_update_patnum(bullet);
}

#define bullet_turn_complete(bullet) \
	bullet_update_patnum(bullet); \
	bullet.speed_cur = bullet.speed_final; \
	if(bullet.u1.turns_done >= bullet_special.turns_max) { \
		bullet.move_flag = BMF_REGULAR; \
	} \
	bullet_velocity_set_from_angle_and_speed(bullet);

enum bullet_bounce_edge_t {
	BBE_LEFT = (1 << 0),
	BBE_RIGHT = (1 << 1),
	BBE_TOP = (1 << 2),
	BBE_BOTTOM = (1 << 3),
};

#define bullet_bounce(bullet, edges) \
	if( \
		((edges & BBE_LEFT) && (bullet.pos.cur.x.v <= to_sp(0.0f))) || \
		((edges & BBE_RIGHT) && (bullet.pos.cur.x.v >= to_sp(PLAYFIELD_W))) \
	) { \
		bullet_turn_x(bullet); \
	} \
	if(\
		((edges & BBE_TOP) && (bullet.pos.cur.y.v <= to_sp(0.0f))) || \
		((edges & BBE_BOTTOM) && (bullet.pos.cur.y.v >= to_sp(PLAYFIELD_H))) \
	) { \
		bullet_turn_y(bullet); \
	}

// Calculates [bullet.velocity] for the special motion types.
void pascal near bullet_update_special(bullet_t near &bullet)
{
	switch(bullet.special_motion) {
	case BSM_DECELERATE_THEN_TURN_AIMED:
		if(bullet.speed_cur.v != to_sp(0.0f)) {
			bullet_velocity_set_from_angle_and_speed(bullet);
			bullet.speed_cur.v--; // -= to_sp(1 / 16.0f)
		} else {
			bullet.u1.turns_done++;
			bullet.angle = iatan2(
				(player_pos.cur.y.v - bullet.pos.cur.y.v),
				(player_pos.cur.x.v - bullet.pos.cur.x.v)
			);
			bullet_turn_complete(bullet);
		}
		break;

	case BSM_DECELERATE_THEN_TURN:
		if(bullet.speed_cur.v != to_sp(0.0f)) {
			bullet_velocity_set_from_angle_and_speed(bullet);
			bullet.speed_cur.v--; // -= to_sp(1 / 16.0f)
		} else {
			bullet.u1.turns_done++;
			bullet.angle += bullet.u2.angle.turn_by;
			bullet_turn_complete(bullet);
		}
		break;

	case BSM_SPEEDUP:
		bullet_velocity_set_from_angle_and_speed(bullet);
		bullet.speed_cur.v += bullet_special.speed_delta.v;
		break;

	case BSM_DECELERATE_TO_ANGLE:
		if(bullet.speed_cur.v != to_sp(0.0f)) {
			bullet_velocity_set_from_angle_and_speed(bullet);
			// >= to_sp(2 / 16.0f) would have been cleaner
			if(bullet.speed_cur.v > to_sp8(1 / 16.0f)) {
				bullet.speed_cur.v += to_sp(-2 / 16.0f);
			} else {
				bullet.speed_cur.set(0.0f);
			}
			if(bullet.speed_cur.v < to_sp8(2.0f)) {
				bullet.angle += (static_cast<int8_t>(
					bullet.u2.angle.target - bullet.angle
				) / 4);
			}
		} else {
			bullet.angle = bullet.u2.angle.target;
			bullet.speed_cur.v = bullet.speed_final.v;
			bullet.move_flag = BMF_REGULAR;
			bullet_velocity_set_from_angle_and_speed(bullet);
		}
		break;

	case BSM_BOUNCE_LEFT_RIGHT:
		bullet_bounce(bullet, (BBE_LEFT | BBE_RIGHT));
		break;

	case BSM_BOUNCE_TOP_BOTTOM:
		bullet_bounce(bullet, (BBE_TOP | BBE_BOTTOM));
		break;

	case BSM_BOUNCE_LEFT_RIGHT_TOP_BOTTOM:
		bullet_bounce(bullet, (BBE_LEFT | BBE_RIGHT | BBE_TOP | BBE_BOTTOM));
		break;

	case BSM_BOUNCE_LEFT_RIGHT_TOP:
		bullet_bounce(bullet, (BBE_LEFT | BBE_RIGHT | BBE_TOP));
		break;

	case BSM_GRAVITY:
		if(stage_frame_mod2) {
			bullet.pos.velocity.y.v += bullet_special.speed_delta;
		}
		break;

#if (GAME == 5)
	case BSM_EXACT_LINEAR:
		bullet.distance.v += bullet.speed_cur.v;
		vector2_at(
			drawpoint,
			bullet.origin.x.v,
			bullet.origin.y.v,
			bullet.distance.v,
			bullet.angle
		);
		bullet.pos.velocity.x.v = (drawpoint.x.v - bullet.pos.cur.x.v);
		bullet.pos.velocity.y.v = (drawpoint.y.v - bullet.pos.cur.y.v);
		break;
#endif
	}
}

#pragma option -zCMAIN__TEXT -zPmain_01
#include "x86real.h"
#include "src/shared/hardware/graphics.hpp"
#include "th04/formats/super.h"
#include "src/main/hardware/grcg.hpp"
#include "th04/main/player/shot.hpp"
#include "th04/main/tile/tile.hpp"
#include "th04/main/scroll.hpp"

// This byte is cleared together with the visible shot state, but no maintained
// code reads it yet. Keep the address-derived name until its role is observed.
extern unsigned char byte_259A7;
#define shot_reset_unknown byte_259A7

extern SPPoint player_option_pos_cur;
extern "C" void near sub_E1F4(void);
#define shot_laser_render sub_E1F4

extern "C" void pascal near tiles_invalidate_around(
	subpixel_t center_y, subpixel_t center_x
);

#include "th04/main/player/bomb.hpp"
#include "th04/main/spark.hpp"
#include "th04/main/frames.h"
#include "th04/sprites/main_pat.h"

// Shared phase counter for the random hit sparks. Every colliding shot or
// laser column advances it; ordinary shots emit on odd values and lasers on
// every fourth value.
extern unsigned char byte_25980;
#define shot_hit_spark_cycle byte_25980

extern unsigned long score_delta;

void near shots_reset(void)
{
	shot_laser_time = 0;
	shot_laser_style = static_cast<shot_laser_style_t>(0);
	shot_time = 0;
	shot_reset_unknown = 0;
}

void near shots_invalidate(void)
{
	register Shot near *shot;
	register int i;

	tile_invalidate_box.x = 16;
	tile_invalidate_box.y = 16;
	shot = shots;
	i = 0;
	for(; i < SHOT_COUNT; (i++, shot++)) {
		if(shot->flag != SF_FREE) {
			tiles_invalidate_around(shot->pos.prev.y.v, shot->pos.prev.x.v);
		}
	}
	if(shot_laser_time >= SHOT_LASER_COOLDOWN_FRAMES) {
		// The laser is drawn as two option-centered columns. The invalidator
		// receives segment-1 coordinates: Y/2 is its center and Y/16 its
		// half-height in pixels.
		tile_invalidate_box.x = 8;
		tile_invalidate_box.y = (shot_laser_bottomcenter.prev.y.v / 16);
		tiles_invalidate_around(
			(shot_laser_bottomcenter.prev.y.v / 2),
			(shot_laser_bottomcenter.prev.x.v + TO_SP(-24))
		);
		tiles_invalidate_around(
			(shot_laser_bottomcenter.prev.y.v / 2),
			(shot_laser_bottomcenter.prev.x.v + TO_SP(24))
		);
	}
}

void near shots_update(void)
{
	register Shot near *shot;
	register shot_alive_t near *alive;
	int i;

	// Rebuild the compact collision cache every frame. Hit-animation shots
	// remain in the main pool but do not enter this cache.
	shots_alive_count = 0;
	shot = shots;
	alive = shots_alive;
	i = 0;
	for(; i < SHOT_COUNT; (i++, shot++)) {
		if(shot->flag >= SF_REMOVE) {
			shot->flag = SF_FREE;
		}
		if(shot->flag == SF_FREE) {
			continue;
		}

		// update_seg1() returns the current X/Y pair in AX/DX.
		shot->pos.update_seg1();
		if(
			(static_cast<int>(_AX) <= TO_SP(-(SHOT_W / 2))) ||
			(static_cast<int>(_AX) >= TO_SP(PLAYFIELD_W + (SHOT_W / 2))) ||
			(static_cast<int>(_DX) <= TO_SP(-(SHOT_H / 2))) ||
			(static_cast<int>(_DX) >= TO_SP(PLAYFIELD_H + (SHOT_H / 2)))
		) {
			shot->flag = SF_REMOVE;
			continue;
		}
		if(shot->flag > SF_ALIVE) {
			// SF_HIT and the following values are both a removal countdown and
			// the animation clock. Advancing the base pattern only at the first
			// value of each cel interval preserves the original cadence.
			shot->flag++;
			if((shot->flag & (HITSHOT_FRAMES_PER_CEL - 1)) == SF_HIT) {
				shot->patnum_base++;
			}
		} else {
			alive->pos.x.v = _AX;
			alive->pos.y.v = _DX;
			alive->shot = shot;
			alive++;
			shots_alive_count++;
			shot->age++;
		}
	}

	if(shot_laser_time != 0) {
		shot_laser_bottomcenter.prev = shot_laser_bottomcenter.cur;
		static_cast<SPPoint &>(shot_laser_bottomcenter.cur) =
			player_option_pos_cur;
		shot_laser_time--;
	}
}

void near shots_render(void)
{
	register Shot near *shot;
	register int i;

	_ES = SEG_PLANE_B;
	grcg_setmode_rmw();
	if(shot_laser_time > SHOT_LASER_COOLDOWN_FRAMES) {
		shot_laser_render();
	}
	shot = &shots[SHOT_COUNT - 1];
	i = 0;
	for(; i < SHOT_COUNT; (i++, shot--)) {
		if((shot->flag == SF_FREE) || (shot->flag >= SF_REMOVE)) {
			continue;
		}

		// Keep the transient 16-bit pattern number in CX across the draw call.
		_CH = 0;
		_CL = static_cast<unsigned char>(shot->patnum_base);
		if(shot->flag == SF_ALIVE) {
			_AL = shot->age;
			_AL &= 1;
			_AL += _CL;
			_CL = _AL;
		}
		_DX = scroll_subpixel_y_to_vram_seg1(
			shot->pos.cur.y.v + TO_SP(PLAYFIELD_TOP - (SHOT_H / 2))
		);
		_AX = (
			(shot->pos.cur.x.v >> 4) + PLAYFIELD_LEFT - (SHOT_W / 2)
		);
		z_super_roll_put_tiny_16x16_raw(_CX);
	}

	// Disable the GRCG after the final shot or laser draw.
	_DX = 0x7C;
	_AL = 0;
	outportb(_DX, _AL);
}

int shots_hittest(void)
{
	int i;
	shot_alive_t near *alive;
	subpixel_t hitbox_left;
	subpixel_t hitbox_top;
	subpixel_t hitbox_width;
	subpixel_t hitbox_height;
	Subpixel laser_x;
	unsigned char hit_count;
	register Shot near *shot;
	register unsigned int total_damage;

	hitbox_left = (shot_hitbox_center.x.v - shot_hitbox_radius.x.v);
	hitbox_top = (shot_hitbox_center.y.v - shot_hitbox_radius.y.v);
	hitbox_width = (shot_hitbox_radius.x.v * 2);
	hitbox_height = (shot_hitbox_radius.y.v * 2);
	total_damage = 0;
	hit_count = 0;
	alive = shots_alive;
	i = 0;
	for(; i < shots_alive_count; (i++, alive++)) {
		// Unsigned subtraction implements both rectangle bounds in one
		// comparison per axis. Values left or above underflow and fail.
		if(
			(static_cast<unsigned int>(alive->pos.x.v - hitbox_left) <=
			 static_cast<unsigned int>(hitbox_width)) &&
			(static_cast<unsigned int>(alive->pos.y.v - hitbox_top) <=
			 static_cast<unsigned int>(hitbox_height))
		) {
			shot = alive->shot;
			shot->flag = SF_HIT;
			shot->pos.velocity.x.v /= 6;
			shot->pos.velocity.y.v /= 6;
			shot->patnum_base = PAT_HITSHOT;
			hit_count++;

			// The divisor is the number of hits seen in this call. Keep the
			// byte truncation before division: simultaneous later hits award
			// progressively less damage.
			total_damage += (
				static_cast<unsigned char>(shot->damage) / hit_count
			);
			shot_hit_spark_cycle++;
			if(shot_hit_spark_cycle & 1) {
				sparks_add_random(
					shot->pos.cur.x, shot->pos.cur.y, TO_SP(8), 1
				);
			}
		}
	}

	if(bombing) {
		if(stage_frame_mod4 == 0) {
			total_damage += 5;
		}
		if(shots_hittest_against_boss) {
			// This divides the accumulated shot and periodic Bomb damage too.
			total_damage /= 4;
		}
	}

	if(
		(stage_frame_mod2 != 0) &&
		(shot_laser_time > SHOT_LASER_COOLDOWN_FRAMES) &&
		(static_cast<unsigned int>(hitbox_top) <=
		 static_cast<unsigned int>(shot_laser_bottomcenter.cur.y.v))
	) {
		// The laser extends from the top of the playfield to its stored
		// bottom Y. Once that reaches the hitbox top, test each option column.
		laser_x.v = (
			shot_laser_bottomcenter.cur.x.v + TO_SP(-PLAYER_OPTION_DISTANCE)
		);
		if(
			static_cast<unsigned int>(laser_x.v - hitbox_left) <=
			static_cast<unsigned int>(hitbox_width)
		) {
			total_damage += 3;
			shot_hit_spark_cycle++;
			if((shot_hit_spark_cycle & 3) == 0) {
				sparks_add_random(
					laser_x, shot_hitbox_center.y, TO_SP(8), 1
				);
			}
		}
		laser_x.v += TO_SP(PLAYER_OPTION_TO_OPTION_DISTANCE);
		if(
			static_cast<unsigned int>(laser_x.v - hitbox_left) <=
			static_cast<unsigned int>(hitbox_width)
		) {
			total_damage += 3;
			shot_hit_spark_cycle++;
			if((shot_hit_spark_cycle & 3) == 0) {
				sparks_add_random(
					laser_x, shot_hitbox_center.y, TO_SP(8), 1
				);
			}
		}
	}

	// Every damage source handled above also contributes to the score delta.
	score_delta += static_cast<unsigned long>(total_damage);
	return total_damage;
}

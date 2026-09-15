#pragma option -zCMAIN__TEXT -zPmain_01

#include "th04/main/player/player.hpp"
#include "th04/main/tile/tile.hpp"
#include "th04/main/drawp.hpp"
#include "th04/math/vector.hpp"

static const unsigned char MISS_EXPLOSION_COUNT = 8;
static const int MISS_EXPLOSION_W = 48;
static const int MISS_EXPLOSION_H = 48;
static const unsigned int MISS_EXPLOSION_RADIUS_VELOCITY = (7 * 16);
static const unsigned char MISS_EXPLOSION_ANGLE_VELOCITY = 8;

extern unsigned char miss_time;
extern unsigned int miss_explosion_radius;
extern unsigned char miss_explosion_angle;
extern SPPoint player_option_pos_prev;

// These are field-level linkage aliases of the existing drawpoint storage.
// The replay scaffold binds them to drawpoint.x and drawpoint.y without
// allocating additional runtime storage.
extern subpixel_t drawpoint_x;
extern subpixel_t drawpoint_y;

extern "C" void pascal near tiles_invalidate_around(
	subpixel_t center_y, subpixel_t center_x
);

void near player_invalidate(void)
{
	unsigned char angle;
	register int i;
	register int radius;

	tile_invalidate_box.y = PLAYER_H;
	if(miss_time != 0) {
		tile_invalidate_box.x = MISS_EXPLOSION_W;
		radius = (miss_explosion_radius + (-MISS_EXPLOSION_RADIUS_VELOCITY));
		i = 0;
		angle = (miss_explosion_angle - MISS_EXPLOSION_ANGLE_VELOCITY);
		for(
			;
			i < MISS_EXPLOSION_COUNT;
			i++, angle += (256 / (MISS_EXPLOSION_COUNT / 2))
		) {
			if(i == (MISS_EXPLOSION_COUNT / 2)) {
				radius /= 2;
				angle = -angle;
			}
			vector2_at(
				drawpoint,
				player_pos.cur.x.v,
				player_pos.cur.y.v,
				radius,
				angle
			);
			if(
				(drawpoint.y.v < TO_SP(PLAYFIELD_TOP - (MISS_EXPLOSION_H / 2))) ||
				(drawpoint.y.v >= TO_SP(PLAYFIELD_BOTTOM - 8)) ||
				(drawpoint.x.v < TO_SP(PLAYFIELD_LEFT - 40)) ||
				(drawpoint.x.v >= TO_SP(PLAYFIELD_RIGHT - (MISS_EXPLOSION_W / 2)))
			) {
				continue;
			}
			tiles_invalidate_around(drawpoint_y, drawpoint_x);
		}
	} else {
		tile_invalidate_box.x = PLAYER_W;
		tiles_invalidate_around(player_pos.prev.y.v, player_pos.prev.x.v);
		tile_invalidate_box.x = (PLAYER_OPTION_W + PLAYER_W + PLAYER_OPTION_W);
		tile_invalidate_box.y = PLAYER_OPTION_H;
		tiles_invalidate_around(
			player_option_pos_prev.y.v,
			player_option_pos_prev.x.v
		);
	}
}

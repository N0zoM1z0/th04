#ifndef TH04_MAIN_PLAYER_SHOT_HPP
#define TH04_MAIN_PLAYER_SHOT_HPP

#include "src/main/player/player.hpp"
#include "src/main/math/randring.hpp"

SPPoint pascal near shot_velocity_set(
	SPPoint near *velocity, unsigned char angle
);

static const int HITSHOT_CELS = 4;
static const int HITSHOT_FRAMES_PER_CEL = 4;
static const int HITSHOT_FRAMES = (HITSHOT_FRAMES_PER_CEL * HITSHOT_CELS);

enum shot_flag_t {
	SF_FREE = 0,
	SF_ALIVE = 1,
	SF_HIT = 2,
	SF_REMOVE = (SF_HIT + HITSHOT_FRAMES),

	_shot_flag_t_FORCE_UINT8 = 0xFF
};

struct Shot {
	shot_flag_t flag;
	char age;
	PlayfieldMotion pos;
	int patnum_base;
	char damage;
	char angle;

	void from_option_l(float offset = 0.0f) {
		this->pos.cur.x -= PLAYER_OPTION_DISTANCE + offset;
	}

	void from_option_r(float offset = 0.0f) {
		this->pos.cur.x += PLAYER_OPTION_DISTANCE + offset;
	}

	void set_random_angle_forwards(
		unsigned char min = -0x48, unsigned char max = -0x38
	) {
		shot_velocity_set(
			(SPPoint near *)&this->pos.velocity,
			randring1_next8_ge_lt(min, max)
		);
	}
};

static const int SHOT_COUNT = 68;

extern unsigned char shot_time;
extern Shot near shots[SHOT_COUNT];
extern Shot near *shot_ptr;
extern char shot_last_id;

extern SPPoint shot_hitbox_center;
extern SPPoint shot_hitbox_radius;
extern bool shots_hittest_against_boss;

struct shot_alive_t {
	SPPoint pos;
	Shot near *shot;
};

extern unsigned int shots_alive_count;
extern shot_alive_t shots_alive[SHOT_COUNT];

Shot near * near shots_add(void);
int shots_hittest(void);

inline int shots_hittest(
	const PlayfieldPoint &center,
	const subpixel_t &radius_x,
	const subpixel_t &radius_y
) {
	shot_hitbox_radius.x.v = radius_x;
	shot_hitbox_radius.y.v = radius_y;
	shot_hitbox_center.x.v = center.x.v;
	shot_hitbox_center.y.v = center.y.v;
	return shots_hittest();
}

void near shots_invalidate(void);
void near shots_render(void);

static const pixel_t SHOT_LASER_W = 8;
static const unsigned int SHOT_LASER_COOLDOWN_FRAMES = 32;

typedef enum {
	SHOT_LASER_CEL_0,
	SHOT_LASER_CEL_1,
	SHOT_LASER_CEL_2,
	SHOT_LASER_CEL_3,
	SHOT_LASER_CEL_4,
	SHOT_LASER_CELS,
} shot_laser_cel_t;

enum shot_laser_style_t {
	SLS_2 = 0,
	SLS_4 = 1,
	SLS_6 = 2,
	SLS_1_4_1 = 3,
	SLS_8 = 4,

	_shot_laser_style_t_FORCE_UINT8 = 0xFF
};

extern unsigned int shot_laser_time;
extern shot_laser_style_t shot_laser_style;
extern uint8_t shot_laser_ring_cycle;
extern PlayfieldMotion shot_laser_bottomcenter;

#define shot_laser_put(left, top, h, cel) \
	_SI = h; \
	shot_laser_put_raw(left, top, cel);
void __fastcall near shot_laser_put_raw(
	screen_x_t left, vram_y_t top, shot_laser_cel_t cel
);

#endif

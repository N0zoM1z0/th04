#ifndef TH04_MAIN_BULLET_BULLET_HPP
#define TH04_MAIN_BULLET_BULLET_HPP

#include "src/main/bullet/types.hpp"
#include "src/main/core/entity.hpp"
#include "th04/main/playfld.hpp"
#include "th04/main/rank.hpp"
#include "src/main/sprites/cels.hpp"

extern "C" {

static const int BMF_DECAY_FRAMES_PER_CEL = 4;
#define BSF_CLOUD_FRAMES (BULLET_CLOUD_CELS * 4)
#define BMF_DECAY_FRAMES (BULLET_DECAY_CELS * BMF_DECAY_FRAMES_PER_CEL)

#define BMF_DECELERATE_BASE_SPEED 4.5f
#define BMF_DECELERATE_THRESHOLD (BMF_DECELERATE_BASE_SPEED - 0.5f)
#define BMF_DECELERATE_FRAMES 32

typedef enum {
	BSF_GRAZEABLE = 0,
	BSF_GRAZED = 1,
	BSF_ACTIVE = 2,
	BSF_CLOUD_BACKWARDS = 3,
	BSF_CLOUD_FORWARDS = 4,
	BSF_CLOUD_END = (BSF_CLOUD_FORWARDS + BSF_CLOUD_FRAMES),

	_bullet_spawn_flag_t_FORCE_UINT8 = 0xFF
} bullet_spawn_flag_t;

typedef enum {
	BMF_DECELERATE = 0,
	BMF_SPECIAL = 1,
	BMF_REGULAR = 2,
	BMF_DECAY = 4,
	BMF_DECAY_END = (BMF_DECAY + BMF_DECAY_FRAMES),

	_bullet_move_flag_t_FORCE_UINT8 = 0xFF
} bullet_move_flag_t;

typedef enum {
	_bullet_special_motion_t_offset = static_cast<int8_t>((GAME - 5) * 0x81),
	BSM_DECELERATE_THEN_TURN_AIMED,
	BSM_DECELERATE_THEN_TURN,
	BSM_SPEEDUP,
	BSM_DECELERATE_TO_ANGLE,
	BSM_BOUNCE_LEFT_RIGHT,
	BSM_BOUNCE_TOP_BOTTOM,
	BSM_BOUNCE_LEFT_RIGHT_TOP_BOTTOM,
	BSM_BOUNCE_LEFT_RIGHT_TOP,
	BSM_GRAVITY,

#if (GAME == 5)
	BSM_EXACT_LINEAR,
#endif

	BSM_NONE = 0xFF,
} bullet_special_motion_t;

union bullet_special_angle_t {
	unsigned char turn_by;
	char target;
	int8_t v;
};

struct bullet_t {
	entity_flag_t flag;
	char age;
	PlayfieldMotion pos;
	// Stored as a byte even though [bullet_group_t] is compiler-sized.
	unsigned char spawn_group;
	int8_t unused;
	SubpixelLength8 speed_cur;
	bullet_angle_t angle;
	bullet_spawn_flag_t spawn_flag;
	bullet_move_flag_t move_flag;
	bullet_special_motion_t special_motion;
	SubpixelLength8 speed_final;
	union {
		unsigned char decelerate_time;
		unsigned char turns_done;
	} u1;
	union {
		SubpixelLength8 decelerate_speed_delta;
		bullet_special_angle_t angle;
	} u2;
	int patnum;

#if (GAME == 5)
	SPPoint origin;
	Subpixel distance;
#endif
};

static const subpixel_t BULLET_KILLBOX_W = TO_SP(8);
static const subpixel_t BULLET_KILLBOX_H = TO_SP(8);
// Directional bullet cels repeat after half a turn because opposite travel
// directions use the same unoriented sprite axis.
#define BULLET_DIRECTION_SPRITE_ANGLE_PERIOD 0x80u
static const bullet_angle_t BULLET_DIRECTION_SPRITE_ANGLE_STEP = (
	BULLET_DIRECTION_SPRITE_ANGLE_PERIOD / BULLET_D_CELS
);

#if (GAME == 5)
#define PELLET_COUNT 180
#define BULLET16_COUNT 220

extern "C++" unsigned char pascal near bullet_patnum_for_angle(
	unsigned int patnum_base, unsigned char angle
);

extern bool bullet_zap_drop_point_items;
#else
#define PELLET_COUNT 240
#define BULLET16_COUNT 200
#endif
#define BULLET_COUNT (PELLET_COUNT + BULLET16_COUNT)

extern bullet_t bullets[BULLET_COUNT];
#define pellets (&bullets[0])
#define bullets16 (&bullets[PELLET_COUNT])

extern union {
	unsigned char turns_max;
	SubpixelLength8 speed_delta;
} bullet_special;

struct BulletTemplate {
	uint8_t spawn_type;
	unsigned char patnum;
	PlayfieldPoint origin;

#if (GAME == 5)
	bullet_group_t group;
	bullet_special_motion_t special_motion;
	unsigned char spread;
	unsigned char spread_angle_delta;
	unsigned char stack;
	SubpixelLength8 stack_speed_delta;
	bullet_angle_t angle;
	SubpixelLength8 speed;

private:
	void set16(unsigned char& val, uint8_t b0, uint8_t b1) {
		reinterpret_cast<uint16_t &>(val) = (b0 | (b1 << 8));
	}

	void set32(
		unsigned char& val,
		uint8_t b0, uint8_t b1, uint32_t b2, uint32_t b3
	) {
		reinterpret_cast<uint32_t &>(val) = (
			b0 | (b1 << 8) | (b2 << 16) | (b3 << 24)
		);
	}

	void set16_for_rank(
		unsigned char& val,
		uint8_t b0_e, uint8_t b1_e,
		uint8_t b0_n, uint8_t b1_n,
		uint8_t b0_h, uint8_t b1_h,
		uint8_t b0_l, uint8_t b1_l
	) {
		reinterpret_cast<uint16_t &>(val) = select_for_rank(
			(b0_e | (b1_e << 8)),
			(b0_n | (b1_n << 8)),
			(b0_h | (b1_h << 8)),
			(b0_l | (b1_l << 8))
		);
	}

public:
	void set_spread(unsigned char count, unsigned char angle_delta) {
		set16(spread, count, angle_delta);
	}

	void set_stack(unsigned char count, float speed_delta) {
		set16(stack, count, to_sp8(speed_delta));
	}

	void set_spread_stack(
		unsigned char spread, unsigned char spread_angle_delta,
		unsigned char stack, float stack_speed_delta
	) {
		set32(this->spread,
			spread, spread_angle_delta, stack, to_sp8(stack_speed_delta)
		);
	}

	void set_stack_for_rank(
		unsigned char count_easy, float speed_delta_easy,
		unsigned char count_normal, float speed_delta_normal,
		unsigned char count_hard, float speed_delta_hard,
		unsigned char count_lunatic, float speed_delta_lunatic
	) {
		set16_for_rank(stack,
			count_easy, to_sp8(speed_delta_easy),
			count_normal, to_sp8(speed_delta_normal),
			count_hard, to_sp8(speed_delta_hard),
			count_lunatic, to_sp8(speed_delta_lunatic)
		);
	}

	void set_spread_for_rank(
		unsigned char count_easy, unsigned char angle_delta_easy,
		unsigned char count_normal, unsigned char angle_delta_normal,
		unsigned char count_hard, unsigned char angle_delta_hard,
		unsigned char count_lunatic, unsigned char angle_delta_lunatic
	) {
		set16_for_rank(spread,
			count_easy, angle_delta_easy,
			count_normal, angle_delta_normal,
			count_hard, angle_delta_hard,
			count_lunatic, angle_delta_lunatic
		);
	}

#else
	PlayfieldPoint velocity;
	bullet_group_t group;
	unsigned char angle;
	SubpixelLength8 speed;
	unsigned char count;
	bullet_template_delta_t delta;
	uint8_t unused_1;
	bullet_special_motion_t special_motion;
	uint8_t unused_2;
#endif
};

extern BulletTemplate bullet_template;
extern bullet_special_angle_t bullet_template_special_angle;

void pascal near bullet_template_tune_easy(void);
void pascal near bullet_template_tune_normal(void);
void pascal near bullet_template_tune_hard(void);
void pascal near bullet_template_tune_lunatic(void);
extern nearfunc_t_near bullet_template_tune;

#if (GAME == 5)
void near bullets_add_regular(void);
void near bullets_add_special(void);
void far bullets_add_regular_far(void);
#else
void pascal near bullets_add_regular_easy(void);
void pascal near bullets_add_regular_normal(void);
void pascal near bullets_add_regular_hard_lunatic(void);
void pascal near bullets_add_special_easy(void);
void pascal near bullets_add_special_normal(void);
void pascal near bullets_add_special_hard_lunatic(void);

extern nearfunc_t_near bullets_add_regular;
extern nearfunc_t_near bullets_add_special;
#endif

void near bullets_add_regular_fixedspeed(void);
void near bullets_add_special_fixedspeed(void);

}

void near bullets_and_gather_invalidate(void);

#if (GAME == 4)
unsigned char pascal near bullet_patnum_for_angle(unsigned char angle);
#endif

#endif

#ifndef TH04_MAIN_ITEM_ITEM_HPP
#define TH04_MAIN_ITEM_ITEM_HPP

#include "src/main/playfld.hpp"
#include "src/main/core/entity.hpp"

enum item_type_t {
#if GAME == 5
	IT_NONE = -2,
#endif
	IT_ENEMY_DROP_NEXT = -1,
	IT_POWER = 0,
	IT_POINT = 1,
	IT_DREAM = 2,
	IT_BIGPOWER = 3,
	IT_BOMB = 4,
	IT_1UP = 5,
	IT_FULLPOWER = 6,
	IT_COUNT,
};

struct item_t {
	entity_flag_t flag;
	// No recovered TH04 item path reads this byte. Keep it because the target
	// ABI places PlayfieldMotion at offset 2 and each pool entry is 20 bytes.
	char unused;
	PlayfieldMotion pos;
	unsigned char type;
	// Spawn paths clear this byte, but no accepted TH04 item path reads it yet.
	// Its meaning therefore remains unknown rather than being guessed.
	char unknown;
	int patnum;
	bool16 pulled_to_player;
};

#define ITEM_W 16
#define ITEM_H 16
#define ITEM_PULL_SPEED 10

static const int ITEM_COUNT = ((GAME == 5) ? 40 : 32);

extern item_t items[ITEM_COUNT];
extern const int ITEM_PATNUM[IT_COUNT];

void pascal near items_add(subpixel_t x, subpixel_t y, item_type_t type);

extern unsigned char item_playperf_raise;
extern unsigned char item_playperf_lower;

#if GAME == 5
extern unsigned int item_point_score_at_full_dream;
#endif

#define ITEM_MISS_COUNT 5
typedef enum {
	MISS_FIELD_LEFT = 0,
	MISS_FIELD_CENTER = 1,
	MISS_FIELD_RIGHT = 2,
	MISS_FIELD_COUNT,
};

extern const Subpixel ITEM_MISS_VELOCITIES[MISS_FIELD_COUNT][2][ITEM_MISS_COUNT];

extern "C" void pascal far items_miss_add(void);

extern unsigned char stage_point_items_collected;
extern unsigned int items_spawned;
extern unsigned int items_collected;

#if GAME == 5
extern unsigned int extend_point_items_collected;
#endif

extern unsigned int total_point_items_collected;
extern unsigned int total_max_valued_point_items_collected;

extern bool items_pull_to_player;

void near items_invalidate();

#endif

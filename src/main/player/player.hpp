#ifndef TH04_MAIN_PLAYER_PLAYER_HPP
#define TH04_MAIN_PLAYER_PLAYER_HPP

#include "src/main/playfield/motion.hpp"

#define PLAYER_W 32
#define PLAYER_H 48

static const pixel_t PLAYER_OPTION_W = 16;
static const pixel_t PLAYER_OPTION_H = 16;
static const pixel_t PLAYER_OPTION_DISTANCE = (
	(PLAYER_W / 2) + (PLAYER_OPTION_W / 2)
);
static const pixel_t PLAYER_OPTION_TO_OPTION_DISTANCE = (
	PLAYER_OPTION_DISTANCE * 2
);

extern PlayfieldMotion player_pos;
void near player_pos_update_and_clamp(void);

static const uint8_t POWER_MIN = 1;
static const uint8_t POWER_MAX = 128;
static const int SHOT_LEVEL_MAX = 9;

extern bool player_is_hit;
extern unsigned char player_invincibility_time;
extern uint8_t power;
extern int power_overflow;
extern uint8_t shot_level;

#endif

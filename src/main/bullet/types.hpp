#ifndef TH04_MAIN_BULLET_TYPES_HPP
#define TH04_MAIN_BULLET_TYPES_HPP

#include "src/main/math/subpixel.hpp"

// TH04 stores one full clockwise turn in an 8-bit angle: 00h points right,
// 40h points down, 80h points left, and C0h points up. Arithmetic wraps at
// 100h by assignment back to an unsigned byte.
typedef unsigned char bullet_angle_t;
#define BULLET_ANGLE_FULL_TURN 0x100
#define BULLET_ANGLE_HALF_TURN 0x80

typedef union {
	bullet_angle_t spread_angle;
	SubpixelLength8 stack_speed;
} bullet_template_delta_t;

#if (GAME == 5)

typedef enum {
	BG_SINGLE = 0,
	BG_SINGLE_AIMED = 1,
	BG_SPREAD = 2,
	BG_SPREAD_AIMED = 3,
	BG_RING = 4,
	BG_RING_AIMED = 5,
	BG_STACK = 6,
	BG_STACK_AIMED = 7,
	BG_SPREAD_STACK = 8,
	BG_SPREAD_STACK_AIMED = 9,
	BG_RING_STACK = 10,
	BG_RING_STACK_AIMED = 11,
	BG_RANDOM_ANGLE = 12,
	BG_RANDOM_ANGLE_AND_SPEED = 13,
	BG_FORCESINGLE = 14,
	BG_FORCESINGLE_AIMED = 15,
} bullet_group_t;

#define BST_GATHER_NORMAL_SPECIAL_MOVE 0xFE
#define BST_GATHER_ONLY 0xFF
#define BST_NORMAL 0x00
#define BST_GATHER_PELLET 0x01
#define BST_CLOUD_FORWARDS 0x02
#define BST_CLOUD_BACKWARDS 0x03
#define BST_NO_DECELERATE 0x10

#else

typedef enum {
	BG_SINGLE = 0x00,
	BG_SINGLE_AIMED = 0x01,
	BG_FORCESINGLE_RANDOM_ANGLE = 0x1A,
	BG_RANDOM_ANGLE = 0x1B,
	BG_RANDOM_ANGLE_AND_SPEED = 0x1C,
	BG_RANDOM_CONSTRAINED_ANGLE_AIMED = 0x1D,
	BG_RING = 0x26,
	BG_RING_AIMED = 0x2C,
	BG_SPREAD = 0x2D,
	BG_SPREAD_AIMED = 0x2E,
	BG_STACK = 0x2F,
	BG_STACK_AIMED = 0x30,
	BG_FORCESINGLE = 0x40,
	BG_FORCESINGLE_AIMED = 0x41,

	_bullet_group_t_FORCE_UINT8 = 0xFF
} bullet_group_t;

#define BST_GATHER_ONLY 0
#define BST_PELLET 1
#define BST_BULLET16 2
#define BST_GATHER_PELLET 3
#define BST_BULLET16_CLOUD_FORWARDS 4
#define BST_BULLET16_CLOUD_BACKWARDS 5

#endif

#endif

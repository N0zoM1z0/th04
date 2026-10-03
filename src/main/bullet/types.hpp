#ifndef TH04_MAIN_BULLET_TYPES_HPP
#define TH04_MAIN_BULLET_TYPES_HPP

#include "src/main/bullet/group_types.hpp"
#include "src/main/math/subpixel.hpp"

typedef union {
	bullet_angle_t spread_angle;
	SubpixelLength8 stack_speed;
} bullet_template_delta_t;

#if (GAME == 5)

#define BST_GATHER_NORMAL_SPECIAL_MOVE 0xFE
#define BST_GATHER_ONLY 0xFF
#define BST_NORMAL 0x00
#define BST_GATHER_PELLET 0x01
#define BST_CLOUD_FORWARDS 0x02
#define BST_CLOUD_BACKWARDS 0x03
#define BST_NO_DECELERATE 0x10

#else

#define BST_GATHER_ONLY 0
#define BST_PELLET 1
#define BST_BULLET16 2
#define BST_GATHER_PELLET 3
#define BST_BULLET16_CLOUD_FORWARDS 4
#define BST_BULLET16_CLOUD_BACKWARDS 5

#endif

#endif

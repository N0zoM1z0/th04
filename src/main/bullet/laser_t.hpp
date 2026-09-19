#ifndef TH04_MAIN_BULLET_LASER_T_HPP
#define TH04_MAIN_BULLET_LASER_T_HPP

#include "src/main/math/subpixel.hpp"

#define THICKLASER_COUNT 2

enum thicklaser_flag_t {
	TF_FREE = 0,
	TF_LINE = 1,
	TF_GROW = 2,
	TF_STATIC = 3,
	TF_SHRINK = 4,
};

struct thicklaser_t {
	thicklaser_flag_t flag;
	int8_t unused_1;
	SPPoint origin;
	int8_t unused_2[4];
	int cur_flag_frame;
	int line_frames;
	int static_frames;
	vc_t col_outline;
	int8_t unused_3;
	pixel_t radius_max;
	pixel_t radius_cur;
	pixel_t radius_speed;
};

extern thicklaser_t thicklaser_template;
extern thicklaser_t thicklasers[THICKLASER_COUNT];

#endif

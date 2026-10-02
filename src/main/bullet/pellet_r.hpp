#ifndef TH04_MAIN_BULLET_PELLET_R_HPP
#define TH04_MAIN_BULLET_PELLET_R_HPP

#include "src/main/bullet/bullet.hpp"
#include "src/main/hardware/planar.hpp"

union pellet_render_t {
	struct {
		screen_x_t left;
		vram_y_t top;
	} top;
	struct {
		vram_offset_t vram_offset;
		uint16_t sprite_offset;
	} bottom;
};

#if (GAME == 5)
// Separate render list for pellets during their delay cloud stage.
extern int pellet_clouds_render_count;
extern bullet_t near *pellet_clouds_render[PELLET_COUNT];
#endif

extern int pellets_render_count;
extern pellet_render_t pellets_render[PELLET_COUNT];

#ifdef TH04P
void far pellets_render_top();
void far pellets_render_bottom();
#else
void near pellets_render_top();
void near pellets_render_bottom();
#endif

#endif

typedef int screen_x_t;
typedef int screen_y_t;
typedef int mswin_tile_amount_t;

static const int MSWIN_H = 16;
static const int DROP_FRAMES_PER_TILE = 2;
static const int DROP_SPEED = 8;

struct window_t {
	mswin_tile_amount_t w;
	mswin_tile_amount_t h;
	int pixel_h(void) const { return (h * MSWIN_H); }
};
extern window_t window;

void pascal near window_rollup_put(screen_x_t left, screen_y_t bottom_tile_top);
void pascal frame_delay(int frames);

#pragma codeseg OP_SETUP_TEXT op_setup_01
#include "src/op/setup/rollup.inl"
#pragma codeseg

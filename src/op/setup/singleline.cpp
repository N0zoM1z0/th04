typedef int screen_x_t;
typedef int screen_y_t;
typedef int pixel_t;
typedef int mswin_tile_amount_t;

static const pixel_t MSWIN_W = 16;
static const pixel_t MSWIN_H = 16;

enum setup_window_patnum_t {
	MSWIN_MIDDLE_TOP = 1,
	MSWIN_MIDDLE_BOTTOM = 3,
	MSWIN_LEFT_TOP = 5,
	MSWIN_LEFT_BOTTOM = 6,
	MSWIN_RIGHT_BOTTOM = 7,
	MSWIN_RIGHT_TOP = 8,
};

struct window_t {
	mswin_tile_amount_t w;
	mswin_tile_amount_t h;
};
extern window_t window;

void far pascal egc_copy_rect_1_to_0_16(
	screen_x_t left, screen_y_t top, pixel_t w, pixel_t h
);
void far pascal super_put(screen_x_t left, screen_y_t top, int patnum);

#pragma codeseg OP_SETUP_TEXT op_setup_01
#include "src/op/setup/singleline.inl"
#pragma codeseg

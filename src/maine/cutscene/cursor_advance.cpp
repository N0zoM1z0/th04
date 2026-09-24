#include "src/shared/hardware/graphics.hpp"
#include "src/shared/hardware/input.hpp"

static const int BOX_LEFT = 80;
static const int BOX_TOP = 320;
static const int BOX_RIGHT = 560;
static const int BOX_BOTTOM = 384;
static const int NAME_W = 64;

struct cursor_t {
	int x;
	int y;
};
extern cursor_t cursor;
extern unsigned char fast_forward;

void near box_1_to_0_animate(void);
void near box_bg_put(void);

#pragma codeseg CUTSCENE_TEXT cursor_advance_01
#include "src/maine/cutscene/cursor_advance.inl"

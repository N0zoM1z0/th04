typedef int screen_x_t;
typedef int screen_y_t;
typedef int pixel_t;

struct screen_point_t {
	screen_x_t x;
	screen_y_t y;
};

struct subpixel_word_t {
	int v;
};

union space_changing_pixel_t {
	subpixel_word_t sp;
	screen_y_t pixel;
};

static const int SUBPIXEL_BITS = 4;

extern const short CosTable8[256];
extern const short SinTable8[256];
int far pascal polar(int center, int radius, int ratio);

#pragma codeseg OP_MUSIC_TEXT polygon_build_01
#include "src/op/music/polygon_build.inl"
#pragma codeseg

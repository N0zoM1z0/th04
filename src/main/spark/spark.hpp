#ifndef TH04_MAIN_SPARK_HPP
#define TH04_MAIN_SPARK_HPP

#include "th04/main/playfld.hpp"
#include "src/main/core/entity.hpp"

struct spark_t {
    entity_flag_t flag;
    unsigned char age;
    PlayfieldMotion center;
    unsigned int angle;
};

static const int SPARK_COUNT = ((GAME == 5) ? 64 : 96);
#define SPARK_COUNT_BUG 96

extern spark_t sparks[SPARK_COUNT];
extern uint16_t spark_ring_offset;

void pascal sparks_add_random(
    Subpixel center_x, Subpixel center_y, subpixel_t radius_min, int count
);
void pascal near sparks_add_circle(
    Subpixel center_x, Subpixel center_y, subpixel_t distance, int count
);

// The original MAIN targets export these three lifecycle entry points with
// C linkage. sparks_invalidate() is intentionally different: its target public
// is the C++-decorated @sparks_invalidate$qv.
extern "C" void near sparks_init(void);
extern "C" void near sparks_update(void);
extern "C" void near sparks_render(void);
void near sparks_invalidate(void);

#endif

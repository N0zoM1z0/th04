#pragma option -zCMAIN_012_TEXT -zPmain_01

#include "compat/rec98/libs/master.lib/pc98_gfx.hpp"
#include "th04/main/frames.h"
#include "th04/main/slowdown.hpp"
#include "th04/main/quit.hpp"
#include "th04/main/score.hpp"
#include "th04/main/playfld.hpp"

extern bool palette_changed;
extern unsigned char bullet_zap;
extern unsigned char circles_color;

// Target-owned storage blocks cleared as 32-bit units by the shared helper.
// The counts are independently pinned by their TH04 BSS structure extents.
enum clear_dword_count_t {
    SHOTS_CLEAR_DWORDS = 0x132,
    ENEMIES_CLEAR_DWORDS = 0x200,
    SPARKS_CLEAR_DWORDS = 0x180,
    BULLETS_CLEAR_DWORDS = 0xB2C,
    CUSTOM_ENTITIES_CLEAR_DWORDS = 0xD0,
    CIRCLES_CLEAR_DWORDS = 0x28,
    ITEMS_CLEAR_DWORDS = 0xA0,
    POINTNUMS_CLEAR_DWORDS = 0x640,
    GATHER_CIRCLES_CLEAR_DWORDS = 0xA8,
};

extern unsigned long shots[SHOTS_CLEAR_DWORDS];
extern unsigned long enemies[ENEMIES_CLEAR_DWORDS];
extern unsigned long sparks[SPARKS_CLEAR_DWORDS];
extern unsigned long bullets[BULLETS_CLEAR_DWORDS];
extern unsigned long custom_entities[CUSTOM_ENTITIES_CLEAR_DWORDS];
extern unsigned long circles[CIRCLES_CLEAR_DWORDS];
extern unsigned long items[ITEMS_CLEAR_DWORDS];
extern unsigned long pointnums[POINTNUMS_CLEAR_DWORDS];
extern unsigned long gather_circles[GATHER_CIRCLES_CLEAR_DWORDS];

struct gather_template_storage_t {
    int center_x;
    int center_y;
    int velocity_x;
    int velocity_y;
    int radius;
    int ring_points;
    unsigned char col;
    unsigned char angle_delta;
};
extern gather_template_storage_t gather_template;

extern "C" void pascal near clear_dwords(void near *dest, unsigned int dwords);

extern "C" void near stage_state_init(void)
{
    frames_unused = 0;
    stage_frame = 0;
    stage_frame_mod2 = 0;
    stage_frame_mod4 = 0;
    stage_frame_mod8 = 0;
    stage_frame_mod16 = 0;
    slowdown_factor = 1;
    quit = Q_KEEP_RUNNING;
    palette_changed = false;
    bullet_zap = 0;
    stage_graze = 0;
    circles_color = 13;

    grc_setclip(
        PLAYFIELD_LEFT,
        PLAYFIELD_TOP,
        (PLAYFIELD_RIGHT - 1),
        (PLAYFIELD_BOTTOM - 1)
    );

    clear_dwords(shots, SHOTS_CLEAR_DWORDS);
    clear_dwords(enemies, ENEMIES_CLEAR_DWORDS);
    clear_dwords(sparks, SPARKS_CLEAR_DWORDS);
    clear_dwords(bullets, BULLETS_CLEAR_DWORDS);
    clear_dwords(custom_entities, CUSTOM_ENTITIES_CLEAR_DWORDS);
    clear_dwords(circles, CIRCLES_CLEAR_DWORDS);
    clear_dwords(items, ITEMS_CLEAR_DWORDS);
    clear_dwords(pointnums, POINTNUMS_CLEAR_DWORDS);
    clear_dwords(gather_circles, GATHER_CIRCLES_CLEAR_DWORDS);

    gather_template.ring_points = 8;
    gather_template.col = 9;
    gather_template.radius = TO_SP(64);
    gather_template.angle_delta = 2;
    gather_template.velocity_x = 0;
    gather_template.velocity_y = 0;
}

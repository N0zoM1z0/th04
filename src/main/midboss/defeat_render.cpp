#pragma option -zCMAIN_012_TEXT -zPmain_01

#include "compat/rec98/libs/master.lib/master.hpp"
#include "compat/rec98/libs/master.lib/pc98_gfx.hpp"
#include "compat/rec98/th03/math/polar.hpp"
#include "th04/main/scroll.hpp"
#include "th04/main/midboss/midboss.hpp"

static const pixel_t DEFEAT_RADIUS_MAX = 48;
static const pixel_t DEFEAT_SPRITE_RADIUS = 16;
static const unsigned char DEFEAT_SPRITES = 16;

extern unsigned char midboss_defeat_angle;

void near midboss_defeat_render(void)
{
    int i;
    subpixel_t length;
    register subpixel_t x;
    register subpixel_t y;

    length = (midboss.phase_frame << 4);
    if(length >= TO_SP(DEFEAT_RADIUS_MAX)) {
        length = TO_SP(DEFEAT_RADIUS_MAX);
        _AL = midboss_defeat_angle;
        _AL++;
        midboss_defeat_angle = _AL;
    }

    for(i = 0; i < DEFEAT_SPRITES; (i++, midboss_defeat_angle += 0x10)) {
        x = polar(
            midboss.pos.cur.x.v,
            length,
            CosTable8[midboss_defeat_angle]
        );
        y = polar(
            midboss.pos.cur.y.v,
            length,
            SinTable8[midboss_defeat_angle]
        );
        if(
            (y > TO_SP(-DEFEAT_SPRITE_RADIUS)) &&
            (y < TO_SP(PLAYFIELD_H + DEFEAT_SPRITE_RADIUS)) &&
            (x > TO_SP(-DEFEAT_SPRITE_RADIUS)) &&
            (x < TO_SP(PLAYFIELD_W + DEFEAT_SPRITE_RADIUS))
        ) {
            x = ((x >> 4) + (PLAYFIELD_LEFT - DEFEAT_SPRITE_RADIUS));
            y = scroll_subpixel_y_to_vram_seg1(y);
            super_roll_put(x, y, midboss.sprite);
        }
    }
}

#pragma option -zCBOSS_FG_TEXT -zPmain_01

#include "x86real.h"
#include "compat/rec98/libs/master.lib/pc98_gfx.hpp"
#include "th04/formats/super.h"
#include "th04/main/item/item.hpp"
#include "th04/main/scroll.hpp"

extern "C" void pascal near item_splashes_render(void);

extern "C" void pascal near items_render(void)
{
    register item_t near *item;
    register int i;

    _ES = SEG_PLANE_B;
    item_splashes_render();
    item = items;
    i = 0;

    for(; i < ITEM_COUNT; (i++, item++)) {
        if(item->flag != F_ALIVE) {
            continue;
        }
        if(item->pos.cur.y.v <= TO_SP(-(ITEM_H / 2))) {
            continue;
        }
        _DX = scroll_subpixel_y_to_vram_seg1(
            item->pos.cur.y.v + TO_SP(PLAYFIELD_TOP - (ITEM_H / 2))
        );
        _AX = ((item->pos.cur.x.v >> 4) + PLAYFIELD_LEFT - (ITEM_W / 2));
        z_super_roll_put_tiny_16x16_raw(item->patnum);
    }
}

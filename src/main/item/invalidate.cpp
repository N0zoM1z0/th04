#pragma option -zCCIRCLE_TEXT -zPmain_01
#pragma option -k-

#include "th04/main/item/item.hpp"
#include "th04/main/item/splash.hpp"
#include "th04/main/tile/tile.hpp"

extern "C" void pascal near tiles_invalidate_around(const SPPoint center);

void near items_invalidate(void)
{
    *reinterpret_cast<unsigned long near *>(&tile_invalidate_box) = (
        (static_cast<unsigned long>(ITEM_W) << 16) | ITEM_H
    );

    {
        register item_t near *item;
        register int items_left;

        item = items;
        items_left = ITEM_COUNT;
        do {
            if(item->flag != F_FREE) {
                tiles_invalidate_around(item->pos.prev);
            }
            item++;
        } while(--items_left);
    }

    {
        register item_splash_t near *splash;
        register int splashes_left;

        splash = item_splashes;
        splashes_left = ITEM_SPLASH_COUNT;
        do {
            if(splash->flag != F_FREE) {
                tile_invalidate_box.y = tile_invalidate_box.x = (
                    (static_cast<unsigned int>(splash->radius_prev.v) >> 3) + 1
                );
                tiles_invalidate_around(splash->center);
            }
            splash++;
        } while(--splashes_left);
    }
}

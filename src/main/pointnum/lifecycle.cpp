#pragma option -zCCIRCLE_TEXT -zPmain_01 -k-

#include "compat/rec98/th02/main/entity.hpp"
#include "th04/main/pointnum/pointnum.hpp"
#include "th04/main/tile/tile.hpp"

enum {
    POINTNUM_W = 8,
    POINTNUM_H = 8,
};

extern "C" void pascal near tiles_invalidate_around(
    subpixel_t center_y, subpixel_t center_x
);

void pascal near pointnums_init(void)
{
    pointnum_white_p = 0;
    pointnum_yellow_p = 0;
}

void near pointnums_invalidate(void)
{
    register pointnum_t near *p;
    #define count _DI

    tile_invalidate_box.y = POINTNUM_H;
    p = pointnums;
    count = POINTNUM_COUNT;

loop:
    if(p->flag != F_FREE) {
        tile_invalidate_box.x = p->width;
        _AX = p->center_cur.x.v;
        if(p->times_2 != false) {
            _AX += to_sp(POINTNUM_TIMES_2_W / 2);
        }
        tiles_invalidate_around(p->center_prev_y.v, _AX);
    }

    p++;
    if(--count != 0) {
        goto loop;
    }

    #undef count
}

void pascal near pointnums_update(void)
{
    register pointnum_t near *p;
    #define alive reinterpret_cast<pointnum_t near * near *>(_BX)
    #define count _DI
    #define flag reinterpret_cast<uint8_t near &>(p->flag)

    pointnum_first_yellow_alive = 0;
    _BX = reinterpret_cast<uint16_t>(pointnums_alive);
    p = pointnums;
    count = POINTNUM_COUNT;

loop:
    if(flag == F_FREE) {
        goto next;
    }
    if(flag == F_REMOVE) {
        flag = F_FREE;
        goto next;
    }

    _CL = p->age;
    _AX = p->center_cur.y.v;
    p->center_prev_y.v = _AX;
    if(_CL >= POINTNUM_POPUP_FRAMES) {
        _AX -= to_sp(POINTNUM_POPUP_DISTANCE / POINTNUM_POPUP_FRAMES);
    }
    p->center_cur.y.v = _AX;

    if(static_cast<int>(_AX) <= to_sp(-POINTNUM_H / 2)) {
        flag = F_REMOVE;
        goto next;
    }

    _CL++;
    p->age = _CL;
    if(_CL > POINTNUM_FRAMES) {
        flag = F_REMOVE;
        goto next;
    }

    *alive = p;
    if((count <= POINTNUM_YELLOW_COUNT) && (pointnum_first_yellow_alive == 0)) {
        pointnum_first_yellow_alive = p;
    }
    _BX += sizeof(pointnum_t near *);

next:
    p++;
    if(--count != 0) {
        goto loop;
    }
    *alive = 0;

    #undef flag
    #undef count
    #undef alive
}

#pragma option -k.

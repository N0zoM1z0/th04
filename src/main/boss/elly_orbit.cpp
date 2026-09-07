#ifndef TH04_ELLY_MAIN034_COMBINED
#pragma option -a
#pragma option -zCMAIN_034_TEXT -zPmain_03

#include "compat/rec98/libs/master.lib/master.hpp"
#include "compat/rec98/th03/math/polar.hpp"
#include "th04/main/boss/boss.hpp"

#endif

extern int elly_orbit_frame;

extern "C" void near elly_orbit_update(void)
{
    if(elly_orbit_frame < 128) {
        boss.pos.prev.x.v += 8;
        boss.angle = 96;
    } else if(elly_orbit_frame < 256) {
        boss.angle--;
    } else if(elly_orbit_frame < 384) {
        goto move_left;
    } else if(elly_orbit_frame < 512) {
        boss.pos.prev.x.v += 8;
        boss.angle = 32;
    } else if(elly_orbit_frame < 640) {
        boss.angle++;
    } else if(elly_orbit_frame < 768) {
    move_left:
        boss.pos.prev.x.v -= 8;
    } else if(elly_orbit_frame >= 768) {
        boss.pos.prev.x.v += 8;
        boss.angle = 96;
        elly_orbit_frame = 0;
    }

    boss.pos.cur.x.v = polar(
        TO_SP(192), boss.pos.prev.x.v, CosTable8[boss.angle]
    );
    boss.pos.cur.y.v = polar(
        TO_SP(96), boss.pos.prev.x.v, SinTable8[boss.angle]
    );
}

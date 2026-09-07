#ifndef TH04_ELLY_MAIN034_COMBINED
#pragma option -a
#pragma option -zCMAIN_034_TEXT -zPmain_03

#include "compat/rec98/libs/master.lib/master.hpp"
#include "th04/main/boss/boss.hpp"
#include "th04/main/player/player.hpp"

#endif

extern unsigned char elly_scythe_mode;
extern unsigned char elly_scythe_flag;
extern unsigned int elly_scythe_frame;
extern unsigned char elly_scythe_angle;
extern unsigned char elly_scythe_speed;
extern volatile signed char elly_scythe_turn;

extern "C" void near elly_scythe_init(void)
{
    elly_scythe_speed = 8;
    elly_scythe_angle = iatan2(
        (player_pos.cur.y.v - boss.pos.cur.y.v),
        (player_pos.cur.x.v - boss.pos.cur.x.v)
    );
    elly_scythe_mode = 1;
    elly_scythe_frame = 0;
    elly_scythe_flag = 0;
    elly_scythe_turn = 0;
}

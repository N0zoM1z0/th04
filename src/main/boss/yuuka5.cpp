#pragma option -zCB4M_UPDATE_TEXT -zPmain_03

#define TH04_YUUKA5_COMBINED 1
#include "compat/rec98/libs/master.lib/master.hpp"
#include "compat/rec98/libs/master.lib/pc98_gfx.hpp"
#include "src/shared/hardware/v_colors.hpp"
#include "th04/sprites/main_pat.h"
#include "th04/main/frames.h"
#include "th04/main/boss/boss.hpp"
#include "th04/main/circle.hpp"
#include "th04/main/bullet/laser_t.hpp"
#include "th04/main/gather.hpp"
#include "th04/main/player/player.hpp"
#include "th04/main/rank.hpp"
#include "th04/math/randring.hpp"
#include "th04/snd/snd.h"

#pragma codeseg B4M_UPDATE_TEXT main_03
#pragma option -a

#include "th04/y5p1.cpp"
#include "th04/y5p2.cpp"

#undef TH04_YUUKA5_COMBINED

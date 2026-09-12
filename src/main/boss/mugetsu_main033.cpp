// Physical MAIN_033 Mugetsu producer. The included logical sources keep their
// standalone replay profiles when TH04_MUGETSU_MAIN033_COMBINED is undefined.
#pragma option -zCMAIN_033_TEXT -zPmain_03
#pragma option -3
#pragma option -b-
#pragma option -d
#pragma option -ml
#pragma option -Z
#pragma option -O
#define TH04_MUGETSU_MAIN033_COMBINED 1

#include "compat/rec98/libs/master.lib/master.hpp"
#include "compat/rec98/th02/v_colors.hpp"
#include "th04/sprites/main_pat.h"
#include "th04/main/frames.h"
#include "th04/main/boss/boss.hpp"
#include "th04/main/player/player.hpp"
#include "th04/main/gather.hpp"
#include "th04/main/circle.hpp"
#include "th04/math/randring.hpp"
#include "th04/snd/snd.h"

#pragma option -a2
#include "th04/m5pre.cpp"
#include "th04/m5tr0.cpp"

#pragma option -a2
#pragma option -O-
#include "th04/m5tr12.cpp"

#pragma option -a2
#pragma option -O
#include "th04/m5p1.cpp"

#pragma option -a2
#include "th04/m5late.cpp"

#include "src/shared/platform/types.hpp"
#include "src/shared/hardware/graphics.hpp"
#include "src/shared/sound/api.hpp"

typedef void (near pascal *near menu_unput_and_put_func_t)(int sel, vc2 col);

extern int8_t menu_sel;
extern int8_t in_option;
extern bool extra_unlocked;
extern menu_unput_and_put_func_t menu_unput_and_put;

static const int MC_EXTRA = 1;
static const vc2 COL_INACTIVE = 1;
static const vc2 COL_ACTIVE = 8;

#pragma codeseg OP_MAIN_TEXT menu_sel_update_01
#include "src/op/main/menu_sel_update.inl"
#pragma codeseg

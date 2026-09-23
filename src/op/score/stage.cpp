// OP SCORE_TEXT high-score stage renderer.
#include "src/shared/platform/types.hpp"
#include "src/shared/hardware/graphics.hpp"

enum {
    g_NONE = 0xFF,
    g_HISCORE_STAGE_EMPTY = 0xEF,
    COL_SHADOW = 14,
    COL_STAGE = 7,
};

#pragma codeseg SCORE_TEXT op_01
#include "src/op/score/stage_put.inl"
#pragma codeseg

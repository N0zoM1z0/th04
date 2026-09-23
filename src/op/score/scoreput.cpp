// OP SCORE_TEXT two-column score digit renderer.
#include "src/op/score/scoredat.hpp"
#include "src/shared/hardware/graphics.hpp"

#pragma codeseg SCORE_TEXT op_01
void pascal near scores_put(screen_y_t top, int place)
#include "src/op/score/scores_put.inl"
#pragma codeseg

// MAINE SCORE_TEXT score-entry row renderer.
#include "src/maine/score/scoredat.hpp"
#include "src/shared/platform/types.hpp"
#include "src/shared/hardware/graphics.hpp"

extern unsigned char entered_place;
extern int playchar;

void pascal near score_put(int place, unsigned char rendered_playchar);
void pascal near stage_put(int place, int rendered_playchar, int gaiji);

#pragma codeseg SCORE_TEXT score_01
#include "src/maine/score/place_row_put.inl"
#pragma codeseg

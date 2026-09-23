// MAINE SCORE_TEXT score renderer, compiled independently for decoded acceptance.
#include "src/maine/score/scoredat.hpp"
#include "src/shared/platform/types.hpp"
#include "src/shared/hardware/graphics.hpp"

extern unsigned char entered_place;
extern int playchar;

enum { PLAYCHAR_REIMU = 0 };

#pragma codeseg SCORE_TEXT score_01
#include "src/maine/score/score_put.inl"
#pragma codeseg

// MAINE SCORE_TEXT registration name and cursor renderer.
#include "src/maine/score/scoredat.hpp"
#include "src/shared/platform/types.hpp"
#include "src/shared/hardware/graphics.hpp"

// SCORE_TEXT-local EGC copy helper, maintained separately from this owner.
void pascal near score_rect_copy(int left, int top, int width, int height);

#pragma codeseg SCORE_TEXT score_01
#include "src/maine/score/name_cursor.inl"
#pragma codeseg

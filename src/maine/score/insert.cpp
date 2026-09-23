#include "src/maine/score/scoredat.hpp"
#include "src/shared/platform/types.hpp"
#include "src/shared/config/resident.hpp"

extern unsigned char entered_place;

#pragma codeseg SCORE_TEXT score_01
#include "src/maine/score/score_insert.inl"
#pragma codeseg

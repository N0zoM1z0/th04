#include "src/shared/memory/hmem.hpp"

extern unsigned char far *box_bg;

#pragma codeseg CUTSCENE_TEXT cutscene_01
#include "src/maine/cutscene/box_bg_free.inl"
#pragma codeseg

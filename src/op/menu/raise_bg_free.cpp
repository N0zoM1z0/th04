#include "src/shared/memory/hmem.hpp"

extern unsigned char far *raise_bg[2];

#pragma codeseg OP_01_TEXT op_01
#include "src/op/menu/raise_bg_free.inl"
#pragma codeseg

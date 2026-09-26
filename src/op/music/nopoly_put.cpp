#include "src/shared/platform/x86.hpp"
#include "src/shared/platform/pc98.hpp"

extern unsigned char __seg *nopoly_B;

#pragma codeseg OP_MUSIC_TEXT nopoly_put_01
#include "src/op/music/nopoly_put.inl"
#pragma codeseg

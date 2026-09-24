#include "src/shared/memory/hmem.hpp"

extern unsigned char __seg *nopoly_B;
extern unsigned char far *VRAM_PLANE_B;

#pragma codeseg OP_MUSIC_TEXT op_music_01
#include "src/op/music/nopoly_snap.inl"
#pragma codeseg

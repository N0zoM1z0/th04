#pragma option -zCSHARED -k-

#include <dos.h>


#define FLAGS_ZERO (_FLAGS & 0x40)
#include "src/shared/hardware/bgimage.hpp"
#include "src/shared/memory/hmem.hpp"

enum {
    BGIMAGE_PLANE_SIZE = 32000,
    BGIMAGE_SEG_B = 0xA800,
    BGIMAGE_SEG_R = 0xB000,
    BGIMAGE_SEG_G = 0xB800,
    BGIMAGE_SEG_E = 0xE000,
    BGIMAGE_PLANE_COUNT = 4
};

// TC86's ordinary C++ copy surfaces do not emit this 386 string instruction.
// Independent TH05 OP/MAINE targets preserve this exact low-level producer
// architecture, including the segment-stack order and REP MOVSD loop.
#define bgimage_push() asm { \
    push BGIMAGE_SEG_E; \
    push word ptr [bgimage.E]; \
    push BGIMAGE_SEG_G; \
    push word ptr [bgimage.G]; \
    push BGIMAGE_SEG_R; \
    push word ptr [bgimage.R]; \
    push BGIMAGE_SEG_B; \
    push word ptr [bgimage.B]; \
}

#define bgimage_copy_plane() { \
    _SI = 0; \
    _DI = 0; \
    _CX = (BGIMAGE_PLANE_SIZE / sizeof(unsigned long)); \
    asm { rep movsd; } \
}

void bgimage_snap(void)
{
    if(bgimage.B == 0) {
        bgimage.B = reinterpret_cast<unsigned char __seg *>(hmem_allocbyte(BGIMAGE_PLANE_SIZE));
        bgimage.R = reinterpret_cast<unsigned char __seg *>(hmem_allocbyte(BGIMAGE_PLANE_SIZE));
        bgimage.G = reinterpret_cast<unsigned char __seg *>(hmem_allocbyte(BGIMAGE_PLANE_SIZE));
        bgimage.E = reinterpret_cast<unsigned char __seg *>(hmem_allocbyte(BGIMAGE_PLANE_SIZE));
    }

    _DL = BGIMAGE_PLANE_COUNT;
    asm { push ds; }
    bgimage_push();
    do {
        asm { pop es; }
        asm { pop ds; }
        bgimage_copy_plane();
        _DL--;
    } while(!FLAGS_ZERO);
    asm { pop ds; }
}

void bgimage_put(void)
{
    _DL = BGIMAGE_PLANE_COUNT;
    asm { push ds; }
    bgimage_push();
    do {
        asm { pop ds; }
        asm { pop es; }
        bgimage_copy_plane();
        _DL--;
    } while(!FLAGS_ZERO);
    asm { pop ds; }
}

// Both TH04 and TH05 place bgimage_free() at the next even SHARED offset.
// Express the historical assembler alignment symbolically; do not emit a byte.
asm {
    SHARED segment byte public use16 'CODE';
    even;
    SHARED ends;
}

void bgimage_free(void)
{
    if(bgimage.B != 0) {
        hmem_free(bgimage.B);
        hmem_free(bgimage.R);
        hmem_free(bgimage.G);
        hmem_free(bgimage.E);
        bgimage.B = 0;
    }
}

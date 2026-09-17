#pragma option -zCSHARED -k-

#include <dos.h>
#include <mem.h>

#include "src/shared/hardware/bgimage.hpp"
#include "src/shared/memory/hmem.hpp"

enum {
    BGIMAGE_PLANE_SIZE = 32000,
    BGIMAGE_SEG_B = 0xA800,
    BGIMAGE_SEG_R = 0xB000,
    BGIMAGE_SEG_G = 0xB800,
    BGIMAGE_SEG_E = 0xE000
};

void bgimage_snap(void)
{
    if(bgimage.B == 0) {
        bgimage.B = reinterpret_cast<unsigned char __seg *>(hmem_allocbyte(BGIMAGE_PLANE_SIZE));
        bgimage.R = reinterpret_cast<unsigned char __seg *>(hmem_allocbyte(BGIMAGE_PLANE_SIZE));
        bgimage.G = reinterpret_cast<unsigned char __seg *>(hmem_allocbyte(BGIMAGE_PLANE_SIZE));
        bgimage.E = reinterpret_cast<unsigned char __seg *>(hmem_allocbyte(BGIMAGE_PLANE_SIZE));
    }

    memcpy((void far *)bgimage.B, MK_FP(BGIMAGE_SEG_B, 0), BGIMAGE_PLANE_SIZE);
    memcpy((void far *)bgimage.R, MK_FP(BGIMAGE_SEG_R, 0), BGIMAGE_PLANE_SIZE);
    memcpy((void far *)bgimage.G, MK_FP(BGIMAGE_SEG_G, 0), BGIMAGE_PLANE_SIZE);
    memcpy((void far *)bgimage.E, MK_FP(BGIMAGE_SEG_E, 0), BGIMAGE_PLANE_SIZE);
}

void bgimage_put(void)
{
    memcpy(MK_FP(BGIMAGE_SEG_B, 0), (void far *)bgimage.B, BGIMAGE_PLANE_SIZE);
    memcpy(MK_FP(BGIMAGE_SEG_R, 0), (void far *)bgimage.R, BGIMAGE_PLANE_SIZE);
    memcpy(MK_FP(BGIMAGE_SEG_G, 0), (void far *)bgimage.G, BGIMAGE_PLANE_SIZE);
    memcpy(MK_FP(BGIMAGE_SEG_E, 0), (void far *)bgimage.E, BGIMAGE_PLANE_SIZE);
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

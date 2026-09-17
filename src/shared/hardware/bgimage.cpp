#pragma option -zCSHARED -k-

#include <dos.h>
#include <mem.h>

#include "compat/rec98/libs/master.lib/master.hpp"
#include "src/shared/hardware/bgimage.hpp"

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
        bgimage.B = HMem<unsigned char>::alloc(BGIMAGE_PLANE_SIZE);
        bgimage.R = HMem<unsigned char>::alloc(BGIMAGE_PLANE_SIZE);
        bgimage.G = HMem<unsigned char>::alloc(BGIMAGE_PLANE_SIZE);
        bgimage.E = HMem<unsigned char>::alloc(BGIMAGE_PLANE_SIZE);
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
        HMem<unsigned char>::free(bgimage.B);
        HMem<unsigned char>::free(bgimage.R);
        HMem<unsigned char>::free(bgimage.G);
        HMem<unsigned char>::free(bgimage.E);
        bgimage.B = 0;
    }
}

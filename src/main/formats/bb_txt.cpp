#pragma option -zCMAIN_01_TEXT -zPmain_01

#include "x86real.h"
#include "compat/rec98/libs/master.lib/master.hpp"
#include "compat/rec98/th04/formats/bb.h"

extern bb_tiles8_t __seg *bb_txt_seg;
extern const char bb_txt_fn[];
extern const char bb_txt2_fn[];

extern "C" {

void pascal near bb_txt_load(void)
{
    bb_txt_seg = reinterpret_cast<bb_tiles8_t __seg *>(
        hmem_allocbyte(BB_SIZE + (BB_SIZE / 2))
    );
    file_ropen(bb_txt_fn);
    file_read(bb_txt_seg, BB_SIZE);
    file_close();

    file_ropen(bb_txt2_fn);
    file_read(MK_FP(bb_txt_seg, BB_SIZE), (BB_SIZE / 2));
    file_close();
}

void pascal near bb_txt_free(void)
{
    if(bb_txt_seg) {
        hmem_free(bb_txt_seg);
        bb_txt_seg = 0;
    }
}

}

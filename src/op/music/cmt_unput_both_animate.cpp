extern "C" {
extern int graph_putsa_fx_func;
void far pascal bgimage_put_rect_16(int left, int top, int w, int h);
}

void near music_update_render_and_flip(void);

#pragma codeseg OP_MUSIC_TEXT op_music_01
#include "src/op/music/cmt_unput_both_animate.inl"
#pragma codeseg

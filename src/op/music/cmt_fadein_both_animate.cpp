extern "C" {
extern int graph_putsa_fx_func;
}

void near cmt_put(void);
void near music_update_render_and_flip(void);

#pragma codeseg OP_MUSIC_TEXT op_music_01
#include "src/op/music/cmt_fadein_both_animate.inl"
#pragma codeseg

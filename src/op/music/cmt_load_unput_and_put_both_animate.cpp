#define true 1
extern unsigned char cmt_shown_initial;

static const int CMT_TITLE_LEFT = 320;
static const int CMT_TITLE_TOP = 64;
static const int RES_X = 640;
static const int CMT_LINES = 20;
static const int GLYPH_H = 16;

void near cmt_unput_both_animate(void);
void pascal near cmt_load(int track);
void near nopoly_B_put(void);
void far pascal bgimage_put_rect_16(int left, int top, int w, int h);
void near cmt_fadein_both_animate(void);
void near cmt_put(void);
void near music_update_render_and_flip(void);

#pragma codeseg OP_MUSIC_TEXT op_music_01
#include "src/op/music/cmt_load_unput_and_put_both_animate.inl"
#pragma codeseg

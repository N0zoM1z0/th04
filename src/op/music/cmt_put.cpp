struct cmt_line_t {
	unsigned char c[40];
};
extern cmt_line_t cmt[20];

static const int CMT_TITLE_LEFT = 320;
static const int CMT_TITLE_TOP = 64;
static const int CMT_COMMENT_LEFT = 320;
static const int CMT_COMMENT_TOP = 80;
static const int CMT_LINES = 20;
static const int GLYPH_H = 16;
static const int COL_CMT_TRACK = 7;
static const int COL_CMT_COMMENT = 7;

void pascal graph_putsa_fx(
	int left, int top, int col, const unsigned char far *str
);

#pragma codeseg OP_MUSIC_TEXT op_music_01
#include "src/op/music/cmt_put.inl"
#pragma codeseg

#include "src/shared/runtime/api.hpp"

static const int CMT_LINE_LENGTH = 38;
static const int CMT_LINE_SIZE = 40;
static const int CMT_LINES = 20;

struct cmt_line_t {
	unsigned char c[CMT_LINE_SIZE];
};
extern cmt_line_t cmt[CMT_LINES];

#pragma codeseg OP_MUSIC_TEXT op_music_01
#include "src/op/music/cmt_load.inl"
#pragma codeseg

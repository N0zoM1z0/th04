typedef unsigned char shiftjis_t;
typedef unsigned int vc2;
typedef int screen_y_t;

static const int CHOICE_LEFT = 48;
static const int CHOICE_TOP = 136;
static const int GLYPH_H = 16;

enum {
	SND_BGM_OFF = 0,
	SND_BGM_FM26 = 1,
	SND_BGM_FM86 = 2,
};

static const shiftjis_t BGM_CHOICE_FM86[] =
	"XeIel¹¹";
static const shiftjis_t BGM_CHOICE_FM26[] =
	"@Wel¹¹@";
static const shiftjis_t BGM_CHOICE_OFF[] =
	"@@¹y³µ@@";

void far pascal graph_putsa_fx(
	int left, int top, int col, const shiftjis_t far *str
);

#pragma codeseg OP_SETUP_TEXT op_setup_01
#include "src/op/setup/bgm_choice_put.inl"
#pragma codeseg

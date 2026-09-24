typedef unsigned char shiftjis_t;
typedef unsigned int vc2;
typedef int screen_y_t;

static const int CHOICE_LEFT = 48;
static const int CHOICE_TOP = 136;
static const int GLYPH_H = 16;

enum {
	SND_SE_OFF = 0,
	SND_SE_FM = 1,
	SND_SE_BEEP = 2,
};

static const shiftjis_t SE_CHOICE_FM[] =
	"@@el¹¹@@";
static const shiftjis_t SE_CHOICE_BEEP[] =
	"@a¹¹@";
static const shiftjis_t SE_CHOICE_OFF[] =
	"@ øÊ¹³µ @";

void far pascal graph_putsa_fx(
	int left, int top, int col, const shiftjis_t far *str
);

#pragma codeseg OP_SETUP_TEXT op_setup_01
#include "src/op/setup/se_choice_put.inl"
#pragma codeseg

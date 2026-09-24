typedef unsigned char shiftjis_t;

enum {
	HELP_TOP = 136,
	HELP_LEFT = 208,
	HELP_LINES = 9,
	GLYPH_H = 16,
	V_WHITE = 15,
};

extern shiftjis_t far *BGM_HELP[HELP_LINES];
extern shiftjis_t far *SE_HELP[HELP_LINES];

extern "C" void pascal graph_putsa_fx(
	int left, int top, int col, const shiftjis_t far *str
);

#pragma codeseg OP_SETUP_TEXT op_setup_01
#include "src/op/setup/help_put.inl"
#pragma codeseg

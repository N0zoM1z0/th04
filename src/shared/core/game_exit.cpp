#pragma option -zCSHARED

#include "src/shared/runtime/api.hpp"
#include "src/shared/hardware/graphics.hpp"

#define graph_clear_both() 	graph_accesspage(1); graph_clear(); 	graph_accesspage(0); graph_clear(); 	graph_accesspage(0); graph_showpage(0);

void game_exit(void)
{
	pfend();
	graph_clear_both();

	mem_unassign();
	vsync_end();
	text_clear();
	js_end();
	egc_start();
	bgm_finish();
}

#undef graph_clear_both

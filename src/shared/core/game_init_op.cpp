#pragma option -zCSHARED -3

#include <stddef.h>

#include "src/shared/runtime/api.hpp"
#include "src/shared/hardware/graphics.hpp"
#include "src/shared/hardware/vram_planes.hpp"

extern size_t mem_assign_paras;

#define graph_clear_both() 	graph_accesspage(1); graph_clear(); 	graph_accesspage(0); graph_clear(); 	graph_accesspage(0); graph_showpage(0);

int game_init_op(const unsigned char *pf_fn)
{
	if(mem_assign_dos(mem_assign_paras)) {
		return 1;
	}
	vram_planes_set();
	graph_start();
	graph_clear_both();
	pfsetbufsiz(8192);
	vsync_start();
	key_beep_off();
	text_systemline_hide();
	text_cursor_hide();
	egc_start();
	js_start();

	if(pf_fn[0]) {
		pfstart(pf_fn);
	}
	bgm_init(1024);
	return 0;
}

#undef graph_clear_both

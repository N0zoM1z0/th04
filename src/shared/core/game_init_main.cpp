#pragma option -zCSHARED -3

#include <stddef.h>

#include "src/shared/runtime/api.hpp"
#include "src/shared/hardware/graphics.hpp"
#include "src/shared/hardware/vram_planes.hpp"

extern size_t mem_assign_paras;

int pascal game_init_main(const unsigned char *pf_fn)
{
	if(mem_assign_dos(mem_assign_paras)) {
		return 1;
	}
	pfsetbufsiz(4096);
	vram_planes_set();
	vsync_start();
	egc_start();
	graph_400line();
	js_start();
	pfstart(pf_fn);
	bgm_init(2048);
	return 0;
}

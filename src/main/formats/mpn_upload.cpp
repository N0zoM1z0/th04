#pragma option -zCEND_TEXT -zPmain_01

#include "compat/rec98/libs/master.lib/pc98_gfx.hpp"

extern "C" int pascal mpn_load_palette_show(int slot, const char *fn);
extern "C" void pascal mpn_free(int slot);

// Game-owned MPN renderer still physically lives in the monolithic MAIN object.
extern "C" void pascal far sub_3680(int left, int top, int zero, int image);

extern "C" int pascal near mpn_load(const char *fn)
{
	int tile_x;
	int tile_y;
	int image;
	register int left;
	register int top;

	mpn_load_palette_show(0, fn);
	image = 0;
	tile_x = 0;
	left = 576;
	while(tile_x < 4) {
		tile_y = 0;
		top = 0;
		while(tile_y < 25) {
			graph_accesspage(1);
			sub_3680(left, top, 0, image);
			graph_accesspage(0);
			sub_3680(left, top, 0, image);
			image++;
			tile_y++;
			top += 16;
		}
		tile_x++;
		left += 16;
	}
	mpn_free(0);

	// Historical ABI: TH02/TH04 declare int, but the target returns without
	// assigning AX. Preserve that compiler-visible behavior instead of inventing
	// a return value solely to silence Turbo C++'s warning.
}

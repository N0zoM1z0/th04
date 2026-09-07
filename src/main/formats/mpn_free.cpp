#pragma option -zCSHARED

#include "compat/rec98/libs/master.lib/master.hpp"
#include "compat/rec98/th02/formats/tile.hpp"
#include "th04/formats/mpn.hpp"

void pascal mpn_free(int slot)
{
	mpn_t near &mpn = mpn_slots[slot];
	if(mpn.images) {
		hmem_free(static_cast<mpn_image_t __seg *>(mpn.images));
		mpn.images = nullptr;
	}
}

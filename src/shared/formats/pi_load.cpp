#pragma option -zCSHARED

#include "compat/rec98/th02/formats/pi.h"

int DEFCONV pi_load(int slot, const char far *fn)
{
	pi_free(slot);
	int ret = graph_pi_load_pack(fn, &pi_headers[slot], &pi_buffers[slot]);
	return ret;
}

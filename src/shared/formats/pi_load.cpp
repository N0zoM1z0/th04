#pragma option -zCSHARED

#include "src/shared/formats/pi.hpp"

int PI_CALL pi_load(int slot, const char far *fn)
{
	pi_free(slot);
	int ret = graph_pi_load_pack(fn, &pi_headers[slot], &pi_buffers[slot]);
	return ret;
}

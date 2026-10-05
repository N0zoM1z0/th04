#pragma option -zCSHARED

#include "src/shared/formats/pi.hpp"

#if defined(TH04P)
void PI_CALL pi_free(int slot)
{
	graph_pi_free(&pi_headers[slot], pi_buffers[slot]);
	pi_buffers[slot] = 0;
}
#endif

int PI_CALL pi_load(int slot, const char far *fn)
{
	pi_free(slot);
	int ret = graph_pi_load_pack(fn, &pi_headers[slot], &pi_buffers[slot]);
	return ret;
}

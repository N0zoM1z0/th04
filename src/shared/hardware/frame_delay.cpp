#pragma option -zCSHARED

#include "src/shared/runtime/api.hpp"

void pascal frame_delay(int minimum_vsync_ticks)
{
	// Count1 is a volatile unsigned 16-bit word advanced by the VSync IRQ.
	// Each call resets it: this measures from this call, not an absolute tick.
	// Retain the unsigned-word comparison with the signed argument, including
	// negative arguments converting to large unsigned waits on the DOS ABI.
	vsync_Count1 = 0;
	while(vsync_Count1 < minimum_vsync_ticks) {}
}

#pragma option -zCSHARED

#include "compat/rec98/libs/master.lib/master.hpp"

void pascal frame_delay(int frames)
{
	vsync_Count1 = 0;
	while(vsync_Count1 < frames) {}
}

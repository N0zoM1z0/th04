#pragma option -zCIT_SPL_U_TEXT -zPmain_03

#include <mem.h>
#include "th04/main/item/splash.hpp"

extern unsigned char item_splash_last_id;

void near item_splashes_init(void)
{
	memset(item_splashes, 0, sizeof(item_splashes));
	item_splash_last_id = 0;
}

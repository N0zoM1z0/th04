#include <dos.h>

#include "src/shared/runtime/api.hpp"

// Alias of VSYNC_START/END's saved PIC mask, owned by vsync_irq.asm.
// START stores FBh/FFh and END clears it; Count1 remains an unsigned WORD.
extern volatile unsigned char __cdecl vsync_OwnerMask;

// Keep these as literal macro expressions: TC4J generates different polling
// instructions when the same values are function-local enum constants.
#define GDC_STATUS_PORT 0xA0
#define GDC_VERTICAL_BLANK 0x20

// Original MAIN/OP/MAINE dispatch once on IRQ ownership at entry. Neither
// path clears Count1 or Count2, unlike frame_delay's clear-before-wait.
void TH04_PASCAL vsync_wait(void)
{
	if(vsync_OwnerMask) {
		const unsigned int previous = vsync_Count1;
		while(vsync_Count1 == previous) {
		}
		return;
	}

	// Finish an already active blank before waiting for the next one.
	// Keep both reads and their order; this does not reset either IRQ counter.
	while(inportb(GDC_STATUS_PORT) & GDC_VERTICAL_BLANK) {
	}
	while(!(inportb(GDC_STATUS_PORT) & GDC_VERTICAL_BLANK)) {
	}
}

#undef GDC_VERTICAL_BLANK
#undef GDC_STATUS_PORT

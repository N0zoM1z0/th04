#include <dos.h>

#include "src/shared/runtime/api.hpp"

// Keep these as literal macro expressions: TC4J generates different polling
// instructions when the same values are function-local enum constants.
#define GDC_STATUS_PORT 0xA0
#define GDC_VERTICAL_BLANK 0x20

// Wait for the next PC-98 graphics vertical blank rising edge. This uses the
// GDC status port path; interrupt-backed waiting is a separate runtime owner.
void TH04_PASCAL vsync_wait(void)
{
	// Finish an already active blank before waiting for the next one.
	// Keep both reads and their order; this does not reset either IRQ counter.
	while(inportb(GDC_STATUS_PORT) & GDC_VERTICAL_BLANK) {
	}
	while(!(inportb(GDC_STATUS_PORT) & GDC_VERTICAL_BLANK)) {
	}
}

#undef GDC_VERTICAL_BLANK
#undef GDC_STATUS_PORT

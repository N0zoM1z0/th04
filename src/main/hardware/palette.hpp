#ifndef TH04_MAIN_HARDWARE_PALETTE_HPP
#define TH04_MAIN_HARDWARE_PALETTE_HPP

#include "src/shared/hardware/graphics.hpp"

extern bool palette_changed;

// Updates the actual hardware palette at the end of the frame.
#define palette_settone_deferred(tone) { \
	PaletteTone = tone; \
	palette_changed = true; \
}

#endif

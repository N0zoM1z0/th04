#ifndef TH04_SHARED_HARDWARE_FRAME_DELAY_HPP
#define TH04_SHARED_HARDWARE_FRAME_DELAY_HPP

// Reset the IRQ-owned Count1 word and wait for at least this many logical
// VSync ticks. This requires the interrupt owner; it does not poll the GDC.
void pascal frame_delay(int minimum_vsync_ticks);

#endif

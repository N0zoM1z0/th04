#ifndef TH04_MAIN_HARDWARE_GRCG_HPP
#define TH04_MAIN_HARDWARE_GRCG_HPP

#include "src/shared/hardware/graphics.hpp"

// Direct GRCG mode switching used by TH04 gameplay code.
#define grcg_setmode(mode) \
	outportb(0x7C, mode)

#undef grcg_off
#define grcg_off() \
	outportb(0x7C, 0)

void near grcg_setmode_rmw(void);
void near grcg_setmode_tdw(void);

// These preserve the current GRCG mode and reenable interrupts before return.
#define grcg_setcolor_direct(col) \
	_AH = col; \
	grcg_setcolor_direct_raw();

void near grcg_setcolor_direct_raw(void);
void near grcg_setcolor_direct_seg3_raw(void);

inline uint8_t grcg_tile_from_carry(uint8_t unused) {
	__emit__(0x1A, 0xC0); // SBB AL, AL
	return _AL;
}

inline void grcg_setmode_rmw_inlined(void) {
	_outportb_(0x7C, 0xC0);
}

#define grcg_setcolor_direct_inlined(col) { \
	disable(); \
	_DX = 0x7E; \
	_AH = col; \
	outportb(_DX, grcg_tile_from_carry(_AH >>= 1)); \
	outportb(_DX, grcg_tile_from_carry(_AH >>= 1)); \
	outportb(_DX, grcg_tile_from_carry(_AH >>= 1)); \
	outportb(_DX, grcg_tile_from_carry(_AH >>= 1)); \
	enable(); \
}

inline void grcg_setcolor_direct_constant(vc_t col) {
	disable();
	_DX = 0x7E;
	outportb(_DX, ((col & 0x1) ? 0xFF : (_AL ^= _AL)));
	outportb(_DX, ((col & 0x2) ? 0xFF : ((col & 0x1) ? (_AL ^= _AL) : _AL)));
	outportb(_DX, ((col & 0x4) ? 0xFF : ((col & 0x2) ? (_AL ^= _AL) : _AL)));
	outportb(_DX, ((col & 0x8) ? 0xFF : ((col & 0x4) ? (_AL ^= _AL) : _AL)));
	enable();
}

#endif

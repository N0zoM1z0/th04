#pragma option -zCSHARED -3

#include <dos.h>

#include "src/shared/hardware/graphics.hpp"

extern "C" unsigned __cdecl graph_VramSeg;

static void gaiji_graph_begin(vc2 color)
{
	// Preserve the caller's interrupt flag while selecting GRCG RMW mode.
	asm {
		pushf
		cli
		mov al, 0C0h
		out 07Ch, al
		popf
	}
	for(unsigned plane = 0; plane < 4; plane++) {
		outportb(0x7E, (color & (1u << plane)) ? 0xFF : 0);
	}
	outportb(0x68, 0x0B); // CG dot access
}

static void gaiji_graph_end(void)
{
	outportb(0x68, 0x0A); // CG code access
	outportb(0x7C, 0);    // GRCG off
	// Both original far entries return with ES selecting the graphics plane.
	_ES = graph_VramSeg;
}

static void gaiji_graph_draw_one(unsigned offset, unsigned shift, unsigned c)
{
	// TH04's fixed master-library variant uses an ordinary ADD here.
	const unsigned jis = (c + 0x5680u) & 0xFF7Fu;
	outportb(0xA1, (unsigned char)jis);
	outportb(0xA3, (unsigned char)(jis >> 8));

	for(unsigned row = 0; row < 16; row++) {
		outportb(0xA5, (unsigned char)(row | 0x20));
		const unsigned first = inportb(0xA9);
		outportb(0xA5, (unsigned char)row);
		const unsigned second = inportb(0xA9);
		const unsigned aligned = ((first << 8) | second) >> shift;
		const unsigned spill = (second << 8) >> shift;
		// The original stores a WORD before advancing DI for its spill byte.
		// Keep the WORD store intact when offset is FFFFh; two separate byte
		// pointers would wrap the second byte to offset zero instead.
		unsigned far *dest = (unsigned far *)MK_FP(graph_VramSeg, offset);
		*dest = (aligned >> 8) | (aligned << 8);
		unsigned char far *extra = (unsigned char far *)MK_FP(
			graph_VramSeg, offset + 2u
		);
		*extra = (unsigned char)spill;
		offset += 80u;
	}
}

extern "C" void TH04_PASCAL graph_gaiji_putc(
	screen_x_t left, vram_y_t top, int c, vc2 color
)
{
	gaiji_graph_begin(color);
	const unsigned offset = ((unsigned)top * 80u) + ((unsigned)left >> 3);
	gaiji_graph_draw_one(offset, (unsigned)left & 7u, (unsigned)c);
	gaiji_graph_end();
}

extern "C" void TH04_PASCAL graph_gaiji_puts(
	screen_x_t left, vram_y_t top, pixel_t step,
	const char TH04_PTR *str, vc2 color
)
{
	gaiji_graph_begin(color);
	unsigned offset = (unsigned)top * 80u;
	unsigned cursor = (unsigned)left;
	while(*str) {
		offset += cursor >> 3;
		cursor &= 7u;
		gaiji_graph_draw_one(offset, cursor, (unsigned char)*str++);
		cursor += (unsigned)step;
	}
	gaiji_graph_end();
}

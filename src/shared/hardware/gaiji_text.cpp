#pragma option -zCSHARED -3

#include <dos.h>

#include "src/shared/hardware/graphics.hpp"

extern "C" unsigned __cdecl TextVramSeg = 0xA000u;

// A PC-98 text cell uses one glyph word and one attribute word in separate
// planes. A gaiji occupies two adjacent cells, one per glyph half.
static unsigned gaiji_first_half(unsigned char c)
{
	return (((unsigned)(c & 0x7F)) << 8) | (0x56 + (c >> 7));
}

static unsigned gaiji_row_segment(unsigned y)
{
	return TextVramSeg + (y * 10u);
}

static void gaiji_text_store(unsigned segment, unsigned offset, unsigned value)
{
	volatile unsigned far *cell = (volatile unsigned far *)MK_FP(segment, offset);
	*cell = value;
}

extern "C" void TH04_PASCAL gaiji_putca(
	unsigned x, unsigned y, unsigned c, unsigned atrb
)
{
	const unsigned segment = gaiji_row_segment(y);
	unsigned offset = x << 1;
	const unsigned first = gaiji_first_half((unsigned char)c);
	gaiji_text_store(segment, offset + 0x2000u, atrb);
	gaiji_text_store(segment, offset, first);
	offset += 2u;
	gaiji_text_store(segment, offset + 0x2000u, atrb);
	gaiji_text_store(segment, offset, first | 0x8000u);
	_ES = segment;
}

extern "C" void TH04_PASCAL gaiji_putsa(
	unsigned x, unsigned y, const char TH04_PTR *str, unsigned atrb
)
{
	const unsigned segment = gaiji_row_segment(y);
	const unsigned start = x << 1;
	unsigned offset = start;
	while(*str) {
		const unsigned first = gaiji_first_half((unsigned char)*str++);
		gaiji_text_store(segment, offset, first);
		offset += 2u;
		gaiji_text_store(segment, offset, first | 0x8000u);
		offset += 2u;
	}
	// The original derives its REP count from wrapped DI, not string length.
	unsigned words = ((unsigned)(offset - start)) >> 1;
	offset = start + 0x2000u;
	while(words--) {
		gaiji_text_store(segment, offset, atrb);
		offset += 2u;
	}
	_ES = segment;
}

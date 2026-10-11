#include <dos.h>

#include "src/shared/hardware/graphics.hpp"

extern "C" unsigned int __cdecl PaletteNote;

// PC-98 analog RGB and notebook LCD palette output. Keep the LCD branch's
// original component masks, weighting and hardware polarity query.
static unsigned char component_at_tone(unsigned char component, int tone)
{
	const int base = (component >> 4);
	if(tone <= 100) {
		return (unsigned char)((base * tone) / 100);
	}
	return (unsigned char)(15 - (((15 - base) * (200 - tone)) / 100));
}

static unsigned char lcd_component(unsigned char component, int tone)
{
	const unsigned char invert = (tone > 100) ? 15 : 0;
	const unsigned int scale = (tone > 100) ? (200 - tone) : tone;
	return (unsigned char)((((component ^ invert) * scale) / 100) ^ invert);
}

static unsigned char lcd_level(unsigned char r, unsigned char g,
	unsigned char b, int tone)
{
	const unsigned char mask = (tone > 100) ? 15 : 0;
	// The original masks red's high nibble and blue's low nibble with the
	// inversion byte; green always uses its high nibble.
	r = lcd_component((r >> 4) & mask, tone);
	g = lcd_component(g >> 4, tone);
	b = lcd_component(b & mask, tone);
	unsigned int maximum = (r > g) ? r : g;
	if(b > maximum) {
		maximum = b;
	}
	const unsigned int weighted = ((r * 2) + (g * 4) + b + maximum);
	const int level = (int)((((weighted * 3) / 20) + 1) / 2) - 2;
	return (unsigned char)((level < 0) ? 0 : level);
}

void TH04_PASCAL palette_show(void)
{
	int tone = (int)PaletteTone;
	if(tone < 0) {
		tone = 0;
	} else if(tone > 200) {
		tone = 200;
	}

	if(PaletteNote != 0) {
		outportb(0xF6, 0xA0);
		unsigned char selector = (unsigned char)inportb(0x871E);
		if(selector == 0xFF) {
			selector = (unsigned char)inportb(0xAE8E) >> 2;
		}
		const unsigned char polarity = (selector & 1) ? 0 : 0xFF;
		for(int color = 0; color < 16; color++) {
			const unsigned char level = lcd_level(Palettes[color].v[0],
				Palettes[color].v[1], Palettes[color].v[2], tone) ^ polarity;
			outportb(0xA8, color);
			outportb(0xAE, (level & 1) ? 15 : 0);
			outportb(0xAC, (level & 2) ? 15 : 0);
			outportb(0xAA, (level & 4) ? 15 : 0);
		}
		return;
	}

	for(int color = 0; color < 16; color++) {
		outportb(0xA8, color);
		outportb(0xAC, component_at_tone(Palettes[color].v[0], tone));
		outportb(0xAA, component_at_tone(Palettes[color].v[1], tone));
		outportb(0xAE, component_at_tone(Palettes[color].v[2], tone));
	}
}

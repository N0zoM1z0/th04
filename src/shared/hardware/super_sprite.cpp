// TH04-local BFNT sprite storage and planar PC-98 rendering.
#pragma option -zCSHARED -3

#include <dos.h>

#include "src/shared/hardware/graphics.hpp"
#include "src/shared/hardware/vram_planes.hpp"
#include "src/shared/runtime/api.hpp"

static unsigned bfnt_word(const unsigned char *header, unsigned at)
{
	return (unsigned)header[at] | ((unsigned)header[at + 1u] << 8);
}

static int bfnt_read(int handle, void far *buffer, unsigned count)
{
	unsigned got = 0;
	return !_dos_read(handle, buffer, count, &got) && (got == count);
}

static int bfnt_skip(int handle, unsigned count)
{
	unsigned char scratch[128];
	while (count) {
		unsigned take = (count > sizeof(scratch)) ? sizeof(scratch) : count;
		if (!bfnt_read(handle, scratch, take)) {
			return 0;
		}
		count -= take;
	}
	return 1;
}

static void super_rollback(unsigned first)
{
	while (super_patnum > first) {
		unsigned slot = --super_patnum;
		if (super_patdata[slot]) {
			hmem_free((void __seg *)super_patdata[slot]);
		}
		super_patdata[slot] = 0;
		super_patsize[slot] = 0;
	}
}

extern "C" int TH04_PASCAL super_cancel_pat(int num)
{
	if ((num < 0) || ((unsigned)num >= super_patnum) ||
	    !super_patdata[num]) {
		return -31;
	}
	hmem_free((void __seg *)super_patdata[num]);
	super_patdata[num] = 0;
	super_patsize[num] = 0;
	while (super_patnum && !super_patdata[super_patnum - 1u]) {
		super_patnum--;
	}
	return 0;
}
extern "C" void TH04_PASCAL super_free(void)
{
	super_rollback(0);
	if (super_buffer) {
		hmem_free(super_buffer);
		super_buffer = 0;
	}
}

extern "C" int TH04_PASCAL super_entry_bfnt(const char far *filename)
{
	int handle;
	unsigned char header[32], palette[48], row[128];
	unsigned width, height, start, end, count, bytes_per_row, plane_bytes;
	unsigned first = super_patnum;
	unsigned clear_color = 0;
	unsigned pattern, y, x, pixel, plane, at, slot, color;
	unsigned char has_palette, packed, bit, bits[5];
	void __seg *allocation;
	unsigned char far *data;
	int error = -13;
	if (!filename) {
		return error;
	}
	if (_dos_open(filename, 0, &handle)) {
		return -2;
	}
	if (!bfnt_read(handle, header, sizeof(header)) ||
	    header[0] != 'B' || header[1] != 'F' ||
	    header[2] != 'N' || header[3] != 'T' ||
	    header[4] != 26 || ((header[5] & 127u) != 3u)) {
		goto failed;
	}
	width = bfnt_word(header, 8);
	height = bfnt_word(header, 10);
	start = bfnt_word(header, 12);
	end = bfnt_word(header, 14);
	if (!width || (width & 7u) || (width > 256u) ||
	    !height || (height > 255u) || (end < start) ||
	    ((unsigned long)end - start + 1UL > SUPER_MAXPAT - first)) {
		goto failed;
	}
	count = end - start + 1u;
	bytes_per_row = width >> 3;
	plane_bytes = bytes_per_row * height;
	if ((unsigned long)plane_bytes * 5UL > 65535UL) {
		goto failed;
	}
	if (!bfnt_skip(handle, bfnt_word(header, 28))) {
		goto failed;
	}
	has_palette = header[5] & 128u;
	if (has_palette && !bfnt_read(handle, palette, sizeof(palette))) {
		goto failed;
	}
	if (!super_buffer) {
		super_buffer = hmem_alloc(576u); // Historical 9,216-byte work buffer.
		if (!super_buffer) {
			error = -8;
			goto failed;
		}
	}
	for (pattern = 0; pattern < count; pattern++) {
		allocation = hmem_allocbyte(plane_bytes * 5u);
		if (!allocation) {
			error = -8;
			goto failed;
		}
		data = (unsigned char far *)MK_FP((unsigned)allocation, 0);
		for (y = 0; y < height; y++) {
			if (!bfnt_read(handle, row, width >> 1)) {
				hmem_free(allocation);
				goto failed;
			}
			for (x = 0; x < bytes_per_row; x++) {
				for (plane = 0; plane < 5u; plane++) {
					bits[plane] = 0;
				}
				for (pixel = 0; pixel < 8u; pixel++) {
					packed = row[(x << 2) + (pixel >> 1)];
					color = (pixel & 1u) ? (packed & 15u) : (packed >> 4);
					bit = (unsigned char)(128u >> pixel);
					if (color != clear_color) {
						bits[0] |= bit;
						for (plane = 0; plane < 4u; plane++) {
							if (color & (1u << plane)) {
								bits[plane + 1u] |= bit;
							}
						}
					}
				}
				at = y * bytes_per_row + x;
				for (plane = 0; plane < 5u; plane++) {
					data[plane * plane_bytes + at] = bits[plane];
				}
			}
		}
		slot = super_patnum++;
		super_patdata[slot] = (unsigned)allocation;
		super_patsize[slot] = (bytes_per_row << 8) | height;
	}
	if (has_palette) {
		for (color = 0; color < 16u; color++) {
			// BFNT stores blue, red, green; Palettes stores red, green, blue.
			Palettes[color].v[0] = palette[color * 3u + 1u];
			Palettes[color].v[1] = palette[color * 3u + 2u];
			Palettes[color].v[2] = palette[color * 3u];
		}
	}
	_dos_close(handle);
	return count;

failed:
	super_rollback(first);
	if (!first && super_buffer) {
		hmem_free(super_buffer);
		super_buffer = 0;
	}
	_dos_close(handle);
	return error;
}

extern "C" void TH04_PASCAL super_put(int x, int y, int num)
{
	if ((num < 0) || ((unsigned)num >= super_patnum) ||
	    !super_patdata[num] || !super_patsize[num] ||
	    !VRAM_PLANE_B || !VRAM_PLANE_R || !VRAM_PLANE_G || !VRAM_PLANE_E) {
		return;
	}
	unsigned packed = super_patsize[num];
	unsigned bytes_per_row = packed >> 8;
	unsigned height = packed & 255u;
	unsigned plane_bytes = bytes_per_row * height;
	const unsigned char far *data =
		(const unsigned char far *)MK_FP(super_patdata[num], 0);
	unsigned char far *planes[4] = {
		VRAM_PLANE_B, VRAM_PLANE_R, VRAM_PLANE_G, VRAM_PLANE_E
	};
	const unsigned char far *colors[4] = {
		data + plane_bytes, data + (plane_bytes * 2u),
		data + (plane_bytes * 3u), data + (plane_bytes * 4u)
	};
	// Each destination byte is composed once, including the carry from the
	// preceding source byte at unaligned X positions.
	const unsigned shift = (unsigned)x & 7u;
	const int first_dst_byte = (x - (int)shift) / 8;
	outportb(0x7C, 0);
	const int byte_count = (int)bytes_per_row + (shift != 0u);
	int bx_first = (first_dst_byte < 0) ? -first_dst_byte : 0;
	int bx_end = 80 - first_dst_byte;
	if (bx_end > byte_count) {
		bx_end = byte_count;
	}
	if (bx_first >= bx_end) {
		return;
	}
	unsigned py_first = 0;
	unsigned py_end = height;
	if (y < 0) {
		if (y <= -(int)height) {
			return;
		}
		py_first = (unsigned)-y;
	} else if (y > (400 - (int)height)) {
		if (y >= 400) {
			return;
		}
		py_end = (unsigned)(400 - y);
	}
	for (unsigned py = py_first; py < py_end; py++) {
		const unsigned sy = (unsigned)(y + (int)py);
		const unsigned src_row = py * bytes_per_row;
		const unsigned dst_row = sy * 80u;
		if (!shift) {
			for (unsigned bx = (unsigned)bx_first; bx < (unsigned)bx_end; bx++) {
				const int dst_byte = first_dst_byte + (int)bx;
				const unsigned src_at = src_row + bx;
				const unsigned char mask = data[src_at];
				if (!mask) {
					continue;
				}
				const unsigned dst_at = dst_row + (unsigned)dst_byte;
				if (mask == 0xFFu) {
					for (unsigned plane = 0; plane < 4u; plane++) {
						planes[plane][dst_at] = colors[plane][src_at];
					}
				} else {
					for (unsigned plane = 0; plane < 4u; plane++) {
						unsigned char far *pixel = planes[plane] + dst_at;
						*pixel = (unsigned char)(
							(*pixel & (unsigned char)~mask) |
							(colors[plane][src_at] & mask)
						);
					}
				}
			}
		} else {
			for (unsigned bx = (unsigned)bx_first; bx < (unsigned)bx_end; bx++) {
				const int dst_byte = first_dst_byte + (int)bx;
				const unsigned src_at = src_row + bx;
				const unsigned char mask = (unsigned char)(
					((bx < bytes_per_row) ? (data[src_at] >> shift) : 0u) |
					((bx > 0u) ? ((unsigned)data[src_at - 1u] << (8u - shift)) : 0u)
				);
				if (!mask) {
					continue;
				}
				const unsigned dst_at = dst_row + (unsigned)dst_byte;
				if (mask == 0xFFu) {
					for (unsigned plane = 0; plane < 4u; plane++) {
						const unsigned char color = (unsigned char)(
							((bx < bytes_per_row) ? (colors[plane][src_at] >> shift) : 0u) |
							((bx > 0u) ? ((unsigned)colors[plane][src_at - 1u] << (8u - shift)) : 0u)
						);
						planes[plane][dst_at] = color;
					}
				} else {
					for (unsigned plane = 0; plane < 4u; plane++) {
						unsigned char far *pixel = planes[plane] + dst_at;
						const unsigned char color = (unsigned char)(
							((bx < bytes_per_row) ? (colors[plane][src_at] >> shift) : 0u) |
							((bx > 0u) ? ((unsigned)colors[plane][src_at - 1u] << (8u - shift)) : 0u)
						);
						*pixel = (unsigned char)(
							(*pixel & (unsigned char)~mask) | (color & mask)
						);
					}
				}
			}
		}
	}
}

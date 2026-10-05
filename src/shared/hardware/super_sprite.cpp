// TH04-local BFNT sprite storage and planar PC-98 rendering.
#pragma option -zCSHARED -3

#include <dos.h>

#include "src/shared/hardware/graphics.hpp"
#include "src/shared/hardware/vram_planes.hpp"
#include "src/shared/runtime/api.hpp"

extern "C" void far pascal th04_sprite_unclipped(
	int left, int top, unsigned packed_size, unsigned pattern_segment
);

// Dimension and pattern-range fields are little-endian words. File pattern
// numbers describe an inclusive count; registration appends to the slot table.
static const unsigned BFNT_HEADER_BYTES = 32u;
static const unsigned BFNT_PALETTE_BYTES = 48u;
static const unsigned BFNT_ROW_BUFFER_BYTES = 128u;
static const unsigned BFNT_WIDTH_OFFSET = 8u;
static const unsigned BFNT_HEIGHT_OFFSET = 10u;
static const unsigned BFNT_FIRST_PATTERN_OFFSET = 12u;
static const unsigned BFNT_LAST_PATTERN_OFFSET = 14u;
static const unsigned BFNT_EXTENSION_BYTES_OFFSET = 28u;

static unsigned bfnt_read_le16(const unsigned char *header, unsigned byte_offset)
{
	return (unsigned)header[byte_offset] | ((unsigned)header[byte_offset + 1u] << 8);
}

static int bfnt_read_exact(int handle, void far *buffer, unsigned count)
{
	// A short read is a malformed/truncated resource, including a short read
	// reported without a DOS error by the active PAR member service.
	unsigned bytes_read = 0;
	return !_dos_read(handle, buffer, count, &bytes_read) && (bytes_read == count);
}

static int bfnt_discard_bytes(int handle, unsigned count)
{
	unsigned char scratch[128];
	while (count) {
		unsigned chunk_bytes = (count > sizeof(scratch)) ? sizeof(scratch) : count;
		if (!bfnt_read_exact(handle, scratch, chunk_bytes)) {
			return 0;
		}
		count -= chunk_bytes;
	}
	return 1;
}

static void super_rollback_appended_patterns(unsigned first_slot)
{
	// Release only slots appended by this load. Earlier slots, including
	// any cancelled holes, retain their indices and segment ownership.
	while (super_patnum > first_slot) {
		unsigned slot = --super_patnum;
		if (super_patdata[slot]) {
			hmem_free((void __seg *)super_patdata[slot]);
		}
		super_patdata[slot] = 0;
		super_patsize[slot] = 0;
	}
}

extern "C" int TH04_PASCAL super_cancel_pat(int pattern_slot)
{
	if ((pattern_slot < 0) || ((unsigned)pattern_slot >= super_patnum) ||
	    !super_patdata[pattern_slot]) {
		return -31;
	}
	hmem_free((void __seg *)super_patdata[pattern_slot]);
	super_patdata[pattern_slot] = 0;
	super_patsize[pattern_slot] = 0;
	// Trim trailing holes without moving live patterns or reusing inner holes.
	while (super_patnum && !super_patdata[super_patnum - 1u]) {
		super_patnum--;
	}
	return 0;
}
extern "C" void TH04_PASCAL super_free(void)
{
	super_rollback_appended_patterns(0);
	if (super_buffer) {
		hmem_free(super_buffer);
		super_buffer = 0;
	}
}

extern "C" int TH04_PASCAL super_entry_bfnt(const char far *filename)
{
	// Return the number of appended patterns, or a negative DOS/format/heap
	// status. Preserve existing slots and palette if this load fails.
	int handle;
	unsigned char header[BFNT_HEADER_BYTES], file_palette[BFNT_PALETTE_BYTES],
		packed_row[BFNT_ROW_BUFFER_BYTES];
	unsigned pixel_width, pixel_height, first_file_pattern, last_file_pattern,
		pattern_count, bytes_per_row, plane_bytes;
	unsigned first_slot = super_patnum;
	// This loader treats palette index zero as transparent. It does not read
	// a separate alpha plane from BFNT: it constructs that plane from pixels.
	unsigned transparent_color = 0;
	unsigned file_pattern, source_row, plane_byte_x, pixel_in_byte, plane,
		plane_byte_offset, slot, color;
	unsigned char has_palette, pixel_pair, pixel_bit, plane_bits[5];
	void __seg *pattern_allocation;
	unsigned char far *pattern_planes;
	int error = -13;
	if (!filename) {
		return error;
	}
	if (_dos_open(filename, 0, &handle)) {
		return -2;
	}
	if (!bfnt_read_exact(handle, header, sizeof(header)) ||
	    header[0] != 'B' || header[1] != 'F' ||
	    header[2] != 'N' || header[3] != 'T' ||
	    header[4] != 26 || ((header[5] & 127u) != 3u)) {
		goto failed;
	}
	pixel_width = bfnt_read_le16(header, BFNT_WIDTH_OFFSET);
	pixel_height = bfnt_read_le16(header, BFNT_HEIGHT_OFFSET);
	first_file_pattern = bfnt_read_le16(header, BFNT_FIRST_PATTERN_OFFSET);
	last_file_pattern = bfnt_read_le16(header, BFNT_LAST_PATTERN_OFFSET);
	if (!pixel_width || (pixel_width & 7u) || (pixel_width > 256u) ||
	    !pixel_height || (pixel_height > 255u) || (last_file_pattern < first_file_pattern) ||
	    ((unsigned long)last_file_pattern - first_file_pattern + 1UL > SUPER_MAXPAT - first_slot)) {
		goto failed;
	}
	pattern_count = last_file_pattern - first_file_pattern + 1u;
	bytes_per_row = pixel_width >> 3;
	plane_bytes = bytes_per_row * pixel_height;
	// Each pattern stays within one 16-bit far-pointer offset range: mask,
	// blue, red, green and intensity are five consecutive plane blocks.
	if ((unsigned long)plane_bytes * 5UL > 65535UL) {
		goto failed;
	}
	if (!bfnt_discard_bytes(handle,
		bfnt_read_le16(header, BFNT_EXTENSION_BYTES_OFFSET))) {
		goto failed;
	}
	has_palette = header[5] & 128u;
	if (has_palette && !bfnt_read_exact(handle, file_palette, sizeof(file_palette))) {
		goto failed;
	}
	if (!super_buffer) {
		// Keep the shared scratch owner used by the sprite service. This
		// byte renderer below reads pattern planes without this work buffer.
		super_buffer = hmem_alloc(576u); // Historical 9,216-byte work buffer.
		if (!super_buffer) {
			error = -8;
			goto failed;
		}
	}
	for (file_pattern = 0; file_pattern < pattern_count; file_pattern++) {
		pattern_allocation = hmem_allocbyte(plane_bytes * 5u);
		if (!pattern_allocation) {
			error = -8;
			goto failed;
		}
		pattern_planes = (unsigned char far *)MK_FP((unsigned)pattern_allocation, 0);
		// Consume rows in file order. Four packed bytes contain eight pixels;
		// the high nibble is the left pixel, and bit 7 is the left plane bit.
		for (source_row = 0; source_row < pixel_height; source_row++) {
			if (!bfnt_read_exact(handle, packed_row, pixel_width >> 1)) {
				// This allocation is not registered yet; rollback below can only
				// see completed patterns, so release the partial pattern here.
				hmem_free(pattern_allocation);
				goto failed;
			}
			for (plane_byte_x = 0; plane_byte_x < bytes_per_row; plane_byte_x++) {
				for (plane = 0; plane < 5u; plane++) {
					plane_bits[plane] = 0;
				}
				for (pixel_in_byte = 0; pixel_in_byte < 8u; pixel_in_byte++) {
					pixel_pair = packed_row[(plane_byte_x << 2) + (pixel_in_byte >> 1)];
					color = (pixel_in_byte & 1u) ? (pixel_pair & 15u) : (pixel_pair >> 4);
					pixel_bit = (unsigned char)(128u >> pixel_in_byte);
					if (color != transparent_color) {
						plane_bits[0] |= pixel_bit;
						for (plane = 0; plane < 4u; plane++) {
							if (color & (1u << plane)) {
								plane_bits[plane + 1u] |= pixel_bit;
							}
						}
					}
				}
				plane_byte_offset = source_row * bytes_per_row + plane_byte_x;
				for (plane = 0; plane < 5u; plane++) {
					pattern_planes[plane * plane_bytes + plane_byte_offset] = plane_bits[plane];
				}
			}
		}
		// Publish a slot only after every row succeeds. Geometry packs bytes
		// per row into the high byte and row count into the low byte.
		slot = super_patnum++;
		super_patdata[slot] = (unsigned)pattern_allocation;
		super_patsize[slot] = (bytes_per_row << 8) | pixel_height;
	}
	if (has_palette) {
		// Keep 8-bit components unchanged; palette_show() uses their high
		// nibbles for the analog DAC. Loading updates software state only.
		for (color = 0; color < 16u; color++) {
			// BFNT stores blue, red, green; Palettes stores red, green, blue.
			Palettes[color].v[0] = file_palette[color * 3u + 1u];
			Palettes[color].v[1] = file_palette[color * 3u + 2u];
			Palettes[color].v[2] = file_palette[color * 3u];
		}
	}
	_dos_close(handle);
	return pattern_count;

failed:
	super_rollback_appended_patterns(first_slot);
	// A failed initial load also releases the shared work buffer. Existing
	// patterns require its lifetime to continue when an appended load fails.
	if (!first_slot && super_buffer) {
		hmem_free(super_buffer);
		super_buffer = 0;
	}
	_dos_close(handle);
	return error;
}

extern "C" void TH04_PASCAL super_put(int left, int top, int pattern_slot)
{
	if ((pattern_slot < 0) || ((unsigned)pattern_slot >= super_patnum) ||
	    !super_patdata[pattern_slot] || !super_patsize[pattern_slot] ||
	    !VRAM_PLANE_B || !VRAM_PLANE_R || !VRAM_PLANE_G || !VRAM_PLANE_E) {
		return;
	}
	unsigned packed_size = super_patsize[pattern_slot];
	// High byte: row width in bytes of ONE plane. Low byte: height in rows.
	unsigned bytes_per_row = packed_size >> 8;
	unsigned height = packed_size & 255u;
	// Preserve GRCG-off even for a fully clipped call. Dispatch the ordinary
	// case before constructing the far-pointer arrays needed by clipping.
	outportb(0x7C, 0);
	if (bytes_per_row && height && (bytes_per_row <= 32u) &&
	    (left >= 0) && (top >= 0) &&
	    (left <= (640 - (int)(bytes_per_row * 8u))) &&
	    (top <= (400 - (int)height))) {
		th04_sprite_unclipped(left, top, packed_size, super_patdata[pattern_slot]);
		return;
	}
	unsigned plane_bytes = bytes_per_row * height;
	const unsigned char far *pattern_planes =
		(const unsigned char far *)MK_FP(super_patdata[pattern_slot], 0);
	unsigned char far *vram_planes[4] = {
		VRAM_PLANE_B, VRAM_PLANE_R, VRAM_PLANE_G, VRAM_PLANE_E
	};
	const unsigned char far *color_planes[4] = {
		pattern_planes + plane_bytes, pattern_planes + (plane_bytes * 2u),
		pattern_planes + (plane_bytes * 3u), pattern_planes + (plane_bytes * 4u)
	};
	// For ordinary screen coordinates, clearing the low three bits before
	// signed division gives floor(left/8), including negative placements.
	// Keep the original 16-bit expression order at extreme integer bounds.
	const unsigned pixel_shift = (unsigned)left & 7u;
	const int first_dst_byte = (left - (int)pixel_shift) / 8;
	// Unaligned placement adds one carry byte. span_first/span_end form a
	// half-open interval of destination-span indices, not screen X pixels.
	const int destination_byte_count = (int)bytes_per_row + (pixel_shift != 0u);
	int span_first = (first_dst_byte < 0) ? -first_dst_byte : 0;
	int span_end = 80 - first_dst_byte;
	if (span_end > destination_byte_count) {
		span_end = destination_byte_count;
	}
	if (span_first >= span_end) {
		return;
	}
	unsigned row_first = 0;
	unsigned row_end = height;
	// Clip source rows before drawing. Visible rows map to screen 0..399;
	// VRAM uses an 80-byte stride regardless of this sprite's own row width.
	if (top < 0) {
		if (top <= -(int)height) {
			return;
		}
		row_first = (unsigned)-top;
	} else if (top > (400 - (int)height)) {
		if (top >= 400) {
			return;
		}
		row_end = (unsigned)(400 - top);
	}
	for (unsigned sprite_row = row_first; sprite_row < row_end; sprite_row++) {
		const unsigned screen_row = (unsigned)(top + (int)sprite_row);
		const unsigned source_row_offset = sprite_row * bytes_per_row;
		const unsigned destination_row_offset = screen_row * 80u;
		if (!pixel_shift) {
			// Aligned masks use one source byte per destination. Empty bytes
			// leave VRAM alone; opaque bytes overwrite without a VRAM read.
			for (unsigned span_byte = (unsigned)span_first;
				span_byte < (unsigned)span_end; span_byte++) {
				const int dst_byte = first_dst_byte + (int)span_byte;
				const unsigned source_offset = source_row_offset + span_byte;
				const unsigned char mask = pattern_planes[source_offset];
				if (!mask) {
					continue;
				}
				const unsigned destination_offset = destination_row_offset + (unsigned)dst_byte;
				if (mask == 0xFFu) {
					for (unsigned plane = 0; plane < 4u; plane++) {
						vram_planes[plane][destination_offset] = color_planes[plane][source_offset];
					}
				} else {
					for (unsigned plane = 0; plane < 4u; plane++) {
						unsigned char far *destination_byte = vram_planes[plane] + destination_offset;
						*destination_byte = (unsigned char)(
							(*destination_byte & (unsigned char)~mask) |
							(color_planes[plane][source_offset] & mask)
						);
					}
				}
			}
		} else {
			// A destination byte combines the current byte shifted right and
			// the preceding byte carried left. The final span byte can be one
			// past the source row; the guarded reads contribute only its carry.
			for (unsigned span_byte = (unsigned)span_first;
				span_byte < (unsigned)span_end; span_byte++) {
				const int dst_byte = first_dst_byte + (int)span_byte;
				const unsigned source_offset = source_row_offset + span_byte;
				const unsigned char mask = (unsigned char)(
					((span_byte < bytes_per_row) ?
						(pattern_planes[source_offset] >> pixel_shift) : 0u) |
					((span_byte > 0u) ?
						((unsigned)pattern_planes[source_offset - 1u] << (8u - pixel_shift)) : 0u)
				);
				if (!mask) {
					continue;
				}
				const unsigned destination_offset = destination_row_offset + (unsigned)dst_byte;
				if (mask == 0xFFu) {
					for (unsigned plane = 0; plane < 4u; plane++) {
						const unsigned char color_bits = (unsigned char)(
							((span_byte < bytes_per_row) ?
								(color_planes[plane][source_offset] >> pixel_shift) : 0u) |
							((span_byte > 0u) ?
								((unsigned)color_planes[plane][source_offset - 1u] <<
									(8u - pixel_shift)) : 0u)
						);
						vram_planes[plane][destination_offset] = color_bits;
					}
				} else {
					for (unsigned plane = 0; plane < 4u; plane++) {
						unsigned char far *destination_byte = vram_planes[plane] + destination_offset;
						const unsigned char color_bits = (unsigned char)(
							((span_byte < bytes_per_row) ?
								(color_planes[plane][source_offset] >> pixel_shift) : 0u) |
							((span_byte > 0u) ?
								((unsigned)color_planes[plane][source_offset - 1u] <<
									(8u - pixel_shift)) : 0u)
						);
						*destination_byte = (unsigned char)(
							(*destination_byte & (unsigned char)~mask) | (color_bits & mask)
						);
					}
				}
			}
		}
	}
}

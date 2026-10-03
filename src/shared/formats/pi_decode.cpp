// TH04 packed PI reader: MSB-first commands produce two 4-bit pixels per
// byte (left pixel in the high nibble). The DOS allocation begins with two
// seeded reference rows; the returned image pointer skips those rows.
//
// This service has one static input stream and is not reentrant. Retain the
// 16-bit unsigned fields, 32-bit unsigned long offsets, far/Pascal API, and
// paragraph allocation until the portable backend replaces them explicitly.
#pragma option -zCSHARED -3

#include <dos.h>

#include "src/shared/hardware/graphics.hpp"
#include "src/shared/runtime/api.hpp"

// Copy selectors describe where packed bytes come from. Repeating the
// preceding selector instead starts an adaptive-color literal run.
enum PiCopyMode {
	PI_COPY_PATTERN = 0,
	PI_COPY_PREVIOUS_ROW = 1,
	PI_COPY_TWO_ROWS_BACK = 2,
	PI_COPY_PREVIOUS_ROW_NEXT_PIXEL = 3,
	PI_COPY_PREVIOUS_ROW_PREVIOUS_PIXEL = 4,
	PI_COPY_NONE = -1,
};

static const unsigned PI_PIXELS_PER_BYTE = 2u;
static const unsigned PI_REFERENCE_ROWS = 2u;
static const unsigned PI_PARAGRAPH_SHIFT = 4u;
static const unsigned PI_PARAGRAPH_MASK = 15u;
static const unsigned PI_MAX_RUN_SUFFIX_BITS = 19u;
// Twice the guarded packed allocation: 65,534 paragraphs of 16 bytes.
static const unsigned long PI_MAX_STORAGE_PIXELS = 2097088UL;

struct PiInput {
	int handle;
	unsigned buffer_size, buffer_cursor;
	unsigned char file_buffer[512];
	unsigned char bit_window;
	unsigned bits_remaining;
	int had_error; // Sticky: a zero result from pi_read_bits() can also mean EOF.
	unsigned char color_history[16][16];
};
static PiInput pi_input;

static int pi_read_byte(void)
{
	if (pi_input.buffer_cursor == pi_input.buffer_size) {
		unsigned bytes_read = 0;
		if (_dos_read(pi_input.handle, pi_input.file_buffer,
			sizeof(pi_input.file_buffer), &bytes_read) || !bytes_read) {
			pi_input.had_error = 1;
			return -1;
		}
		pi_input.buffer_size = bytes_read;
		pi_input.buffer_cursor = 0;
	}
	return pi_input.file_buffer[pi_input.buffer_cursor++];
}

static int pi_read_bit(void)
{
	if (!pi_input.bits_remaining) {
		int value = pi_read_byte();
		if (value < 0) {
			return -1;
		}
		pi_input.bit_window = (unsigned char)value;
		pi_input.bits_remaining = 8;
	}
	int bit = (pi_input.bit_window >> 7) & 1;
	pi_input.bit_window <<= 1;
	pi_input.bits_remaining--;
	return bit;
}

static unsigned long pi_read_bits(unsigned count)
{
	unsigned long value = 0;
	while (count--) {
		int bit = pi_read_bit();
		if (bit < 0) {
			return 0;
		}
		value = (value << 1) | (unsigned)bit;
	}
	return value;
}

static int pi_read_be16(void)
{
	// Keep the signed 16-bit return and the caller's negative-result checks.
	// Widening it during a port would change which header values are accepted.
	int high = pi_read_byte();
	int low = pi_read_byte();
	if ((high < 0) || (low < 0)) {
		return -1;
	}
	return (high << 8) | low;
}

static int pi_decode_color(unsigned previous_color)
{
	// Prefix groups select 2, 2, 4, or 8 entries of the previous color's
	// history. Index 15 is most recent; move the decoded color to that end.
	int first_bit = pi_read_bit();
	unsigned index_base, index_bit_count;
	if (first_bit < 0) {
		return -1;
	}
	if (first_bit) {
		index_base = 0;
		index_bit_count = 1;
	} else {
		int second_bit = pi_read_bit();
		if (second_bit < 0) {
			return -1;
		}
		if (!second_bit) {
			index_base = 2;
			index_bit_count = 1;
		} else {
			int third_bit = pi_read_bit();
			if (third_bit < 0) {
				return -1;
			}
			index_base = third_bit ? 8 : 4;
			index_bit_count = third_bit ? 3 : 2;
		}
	}
	unsigned history_index =
		(index_base + (unsigned)pi_read_bits(index_bit_count)) ^ 15u;
	unsigned char decoded_color =
		pi_input.color_history[previous_color][history_index];
	for (unsigned history_slot = history_index; history_slot < 15u; history_slot++) {
		pi_input.color_history[previous_color][history_slot] =
			pi_input.color_history[previous_color][history_slot + 1u];
	}
	pi_input.color_history[previous_color][15] = decoded_color;
	return pi_input.had_error ? -1 : decoded_color;
}

// Normalize each access independently so a packed image can cross 64 KiB.
// byte_offset is relative to the allocation, including its reference rows.
static unsigned char pi_get_packed_byte(
	unsigned allocation_segment, unsigned long byte_offset
)
{
	unsigned segment = allocation_segment +
		(unsigned)(byte_offset >> PI_PARAGRAPH_SHIFT);
	return *(unsigned char far *)MK_FP(segment,
		(unsigned)(byte_offset & PI_PARAGRAPH_MASK));
}

static void pi_set_packed_byte(
	unsigned allocation_segment, unsigned long byte_offset, unsigned char value
)
{
	unsigned segment = allocation_segment +
		(unsigned)(byte_offset >> PI_PARAGRAPH_SHIFT);
	*(unsigned char far *)MK_FP(segment,
		(unsigned)(byte_offset & PI_PARAGRAPH_MASK)) = value;
}

static int pi_decode_pixels(
	unsigned allocation_segment, unsigned width_pixels,
	unsigned long allocation_bytes
)
{
	unsigned previous_color, history_slot;
	for (previous_color = 0; previous_color < 16u; previous_color++) {
		for (history_slot = 0; history_slot < 16u; history_slot++) {
			pi_input.color_history[previous_color][history_slot] =
				(unsigned char)((previous_color + history_slot + 1u) & 15u);
		}
	}
	pi_input.bits_remaining = 0;
	int first_color = pi_decode_color(0);
	int second_color = first_color < 0 ? -1 : pi_decode_color((unsigned)first_color);
	if (second_color < 0) {
		return 0;
	}
	unsigned char seed_pair = (unsigned char)((first_color << 4) | second_color);
	// For even-width images, two reference rows occupy width_pixels bytes.
	// Keep the historical byte formula for odd widths as well.
	for (history_slot = 0; history_slot < width_pixels; history_slot++) {
		pi_set_packed_byte(allocation_segment, history_slot, seed_pair);
	}
	unsigned long write_offset = width_pixels;
	int previous_copy_mode = PI_COPY_NONE;
	while (write_offset < allocation_bytes) {
		unsigned copy_mode = (unsigned)pi_read_bits(2);
		if (pi_input.had_error) {
			return 0;
		}
		if (copy_mode == PI_COPY_PREVIOUS_ROW_NEXT_PIXEL) {
			int extension = pi_read_bit();
			if (extension < 0) {
				return 0;
			}
			copy_mode += (unsigned)extension;
		}
		if (copy_mode == (unsigned)previous_copy_mode) {
			// A repeated selector emits literal pairs instead of a copy run.
			// Preserve the read order even at the end of the allocation.
			int more_literals;
			do {
				int left_color = pi_decode_color(pi_get_packed_byte(
					allocation_segment, write_offset - 1u) & 15u);
				int right_color = left_color < 0 ? -1 :
					pi_decode_color((unsigned)left_color);
				if ((right_color < 0) || (write_offset == allocation_bytes)) {
					return 0;
				}
				pi_set_packed_byte(allocation_segment, write_offset++,
					(unsigned char)((left_color << 4) | right_color));
				more_literals = pi_read_bit();
				if (more_literals < 0) {
					return 0;
				}
			} while (more_literals);
			previous_copy_mode = PI_COPY_NONE;
			continue;
		}

		// k one-bits followed by zero, then k suffix bits, encode a byte
		// count of 2^k + suffix. All copy commands operate on packed pairs.
		unsigned run_suffix_bits = 0;
		int run_prefix_bit;
		while ((run_prefix_bit = pi_read_bit()) == 1) {
			if (++run_suffix_bits > PI_MAX_RUN_SUFFIX_BITS) {
				return 0;
			}
		}
		if (run_prefix_bit < 0) {
			return 0;
		}
		unsigned long run_bytes =
			(1UL << run_suffix_bits) | pi_read_bits(run_suffix_bits);
		if (pi_input.had_error || (run_bytes > allocation_bytes - write_offset)) {
			return 0;
		}
		if (copy_mode == PI_COPY_PATTERN) {
			unsigned char last_pair = pi_get_packed_byte(
				allocation_segment, write_offset - 1u);
			if ((last_pair >> 4) == (last_pair & 15u)) {
				while (run_bytes--) {
					pi_set_packed_byte(allocation_segment, write_offset++, last_pair);
				}
			} else {
				// Unequal colors repeat the preceding two packed bytes,
				// starting with the older byte rather than the last one.
				unsigned char penultimate_pair = pi_get_packed_byte(
					allocation_segment, write_offset - 2u);
				unsigned pair_phase = 0;
				while (run_bytes--) {
					pi_set_packed_byte(allocation_segment, write_offset++,
						pair_phase ? last_pair : penultimate_pair);
					pair_phase ^= 1u;
				}
			}
		} else if ((copy_mode == PI_COPY_PREVIOUS_ROW) ||
			(copy_mode == PI_COPY_TWO_ROWS_BACK)) {
			unsigned distance_bytes = copy_mode == PI_COPY_PREVIOUS_ROW ?
				width_pixels / PI_PIXELS_PER_BYTE : width_pixels;
			if ((distance_bytes == 0) || (write_offset < distance_bytes)) {
				return 0;
			}
			while (run_bytes--) {
				// Read each byte as the run advances: source and destination
				// may overlap. A snapshot copy would change the result.
				pi_set_packed_byte(allocation_segment, write_offset,
					pi_get_packed_byte(allocation_segment,
						write_offset - distance_bytes));
				write_offset++;
			}
		} else {
			// For even widths, selectors 3/4 sample the previous row at
			// x+1/x-1 respectively, joining nibbles of adjacent bytes.
			unsigned long distance_pixels =
				copy_mode == PI_COPY_PREVIOUS_ROW_NEXT_PIXEL ?
				(unsigned long)width_pixels - 1UL : (unsigned long)width_pixels + 1UL;
			unsigned distance_bytes =
				(unsigned)((distance_pixels + 1UL) / 2UL);
			if ((width_pixels < 3u) || (write_offset < distance_bytes)) {
				return 0;
			}
			while (run_bytes--) {
				unsigned char source_pair = pi_get_packed_byte(
					allocation_segment, write_offset - distance_bytes);
				unsigned char next_source_pair = pi_get_packed_byte(
					allocation_segment, write_offset - distance_bytes + 1u);
				pi_set_packed_byte(allocation_segment, write_offset++,
					(unsigned char)((source_pair << 4) | (next_source_pair >> 4)));
			}
		}
		previous_copy_mode = (int)copy_mode;
	}
	return !pi_input.had_error;
}

extern "C" int TH04_PASCAL graph_pi_load_pack(
	const char far *filename, PiHeader far *header, void far *far *image_out
)
{
	int handle;
	unsigned pixel_segment = 0;
	unsigned char __seg *machine_extension = 0;
	unsigned comment_bytes = 0;
	unsigned width_pixels, height_pixels;
	unsigned long allocation_bytes;
	unsigned field_index;
	int field_value, aspect_n, aspect_m, plane;
	unsigned char far *palette;
	if (!header || !image_out) {
		return -13;
	}
	header->comment = 0;
	header->commentlen = 0;
	header->maex = 0;
	header->maexlen = 0;
	*image_out = 0;
	if (_dos_open(filename, 0, &handle)) {
		return -2;
	}
	pi_input.handle = handle;
	pi_input.buffer_size = pi_input.buffer_cursor = pi_input.bits_remaining = 0;
	pi_input.had_error = 0;
	if ((pi_read_byte() != 'P') || (pi_read_byte() != 'i')) {
		goto invalid;
	}
	while ((field_value = pi_read_byte()) >= 0 && field_value != 26) {
		if (comment_bytes == 65535u) {
			goto invalid;
		}
		comment_bytes++;
	}
	if (field_value < 0) {
		goto invalid;
	}
	header->commentlen = comment_bytes;
	// Comment text is counted, not allocated. Skip the following zero-
	// terminated dummy field before reading the binary PI header.
	while ((field_value = pi_read_byte()) > 0) { }
	if (field_value < 0) {
		goto invalid;
	}
	field_value = pi_read_byte();
	if (field_value < 0) {
		goto invalid;
	}
	header->mode = (unsigned char)field_value;
	aspect_n = pi_read_byte();
	aspect_m = pi_read_byte();
	plane = pi_read_byte();
	if ((aspect_n != 0) || (aspect_m != 0) || (plane != 4)) {
		goto invalid;
	}
	header->n = (unsigned char)aspect_n;
	header->m = (unsigned char)aspect_m;
	header->plane = (unsigned char)plane;
	for (field_index = 0; field_index < 4u; field_index++) {
		field_value = pi_read_byte();
		if (field_value < 0) {
			goto invalid;
		}
		header->machine[field_index] = (char)field_value;
	}
	field_value = pi_read_be16();
	if (field_value < 0) {
		goto invalid;
	}
	header->maexlen = (unsigned)field_value;
	if (header->maexlen) {
		machine_extension = (unsigned char __seg *)hmem_allocbyte(header->maexlen);
		if (!machine_extension) {
			goto no_memory;
		}
		header->maex = (void far *)machine_extension;
		for (field_index = 0; field_index < header->maexlen; field_index++) {
			field_value = pi_read_byte();
			if (field_value < 0) {
				goto invalid;
			}
			machine_extension[field_index] = (unsigned char)field_value;
		}
	}
	field_value = pi_read_be16();
	if (field_value < 0) {
		goto invalid;
	}
	width_pixels = (unsigned)field_value;
	field_value = pi_read_be16();
	if (field_value < 0) {
		goto invalid;
	}
	height_pixels = (unsigned)field_value;
	if ((width_pixels < 3u) || (height_pixels == 0) ||
		((unsigned long)height_pixels + PI_REFERENCE_ROWS >
			PI_MAX_STORAGE_PIXELS / (unsigned long)width_pixels)) {
		goto invalid;
	}
	header->xsize = width_pixels;
	header->ysize = height_pixels;
	if (!(header->mode & 0x80u)) {
		// Preserve the raw RGB triplets; PC-98 palette application uses
		// each component's high nibble. Palette omission leaves it intact.
		palette = (unsigned char far *)&header->palette;
		for (field_index = 0; field_index < 48u; field_index++) {
			field_value = pi_read_byte();
			if (field_value < 0) {
				goto invalid;
			}
			palette[field_index] = (unsigned char)field_value;
		}
	}
	allocation_bytes = (unsigned long)width_pixels *
		((unsigned long)height_pixels + PI_REFERENCE_ROWS) / PI_PIXELS_PER_BYTE;
	pixel_segment = (unsigned)hmem_alloc((unsigned)(
		(allocation_bytes + 15UL) >> PI_PARAGRAPH_SHIFT));
	if (!pixel_segment) {
		goto no_memory;
	}
	if (!pi_decode_pixels(pixel_segment, width_pixels, allocation_bytes)) {
		goto invalid;
	}
	*image_out = MK_FP(pixel_segment, width_pixels);
	// Ownership transfers only here. graph_pi_free() uses this pointer's
	// segment to free the entire allocation, including the reference rows.
	_dos_close(handle);
	return 0;

invalid:
	if (pixel_segment) {
		hmem_free((void __seg *)pixel_segment);
	}
	if (machine_extension) {
		hmem_free(machine_extension);
		header->maex = 0;
		header->maexlen = 0;
	}
	_dos_close(handle);
	return -13;
no_memory:
	if (pixel_segment) {
		hmem_free((void __seg *)pixel_segment);
	}
	if (machine_extension) {
		hmem_free(machine_extension);
		header->maex = 0;
		header->maexlen = 0;
	}
	_dos_close(handle);
	return -8;
}

#pragma option -zCSHARED -3

#include <dos.h>

#include "src/shared/runtime/api.hpp"

// Native product heap: all region/block sizes below are 16-byte paragraphs.
// Each header reserves an entire paragraph even though this struct uses only
// six bytes. Payload starts at header_segment + 1 and the public handle is
// that segment value, not a byte offset or an ordinary C pointer.
struct HeapBlockHeader {
	unsigned is_allocated;
	unsigned next_header_segment;
	unsigned reserved_allocation_id; // Retained layout word; always zero, no generation ID.
};

// Blocks grow downward inside [base, limit). Their linked headers run upward
// from first_block to the exclusive limit sentinel, which has no header.
// The untracked lower interval [base, first_block) remains available for growth.
static unsigned heap_base_segment;
static unsigned heap_limit_segment;
static unsigned heap_first_block_segment; // Lowest linked header; limit when empty.
static unsigned heap_dos_owned; // Release the region through DOS only when owned.

static HeapBlockHeader far *heap_header_at_segment(unsigned segment)
{
	return (HeapBlockHeader far *)MK_FP(segment, 0);
}

static void heap_bind_region(unsigned base_segment, unsigned paragraphs, unsigned dos_owned)
{
	heap_base_segment = base_segment;
	heap_limit_segment = base_segment + paragraphs;
	heap_first_block_segment = heap_limit_segment;
	heap_dos_owned = dos_owned;
}

static int heap_assign_available_dos_block(void)
{
	// DOS reports the largest free block in the output word when this oversized
	// request fails. On success that same word is an allocated segment instead;
	// release the unexpected allocation and leave the heap unbound.
	unsigned largest_paragraphs = 0;
	if(_dos_allocmem(0xFFFFu, &largest_paragraphs) == 0) {
		_dos_freemem(largest_paragraphs);
		return 0;
	}
	// Keep 256 paragraphs (4096 bytes) outside the heap for other DOS users.
	if(largest_paragraphs <= 256u) {
		return 0;
	}
	unsigned paragraphs = largest_paragraphs - 256u;
	unsigned base_segment = 0;
	if(_dos_allocmem(paragraphs, &base_segment) != 0) {
		return 0;
	}
	heap_bind_region(base_segment, paragraphs, 1);
	return 1;
}

static unsigned heap_allocate_paragraphs(unsigned paragraphs)
{
	if(paragraphs == 0) {
		return 0;
	}
	if(!heap_base_segment && !heap_assign_available_dos_block()) {
		return 0;
	}
	// Add the header in 16-bit arithmetic and reject wraparound.
	const unsigned block_paragraphs = paragraphs + 1u;
	if(block_paragraphs <= paragraphs) {
		return 0;
	}

	// First fit walks the upward header chain. Split only if the remainder
	// can hold its own header plus at least one payload paragraph; otherwise
	// the single leftover paragraph is absorbed by this allocation.
	unsigned header_segment = heap_first_block_segment;
	unsigned allocated_header_segment = 0;
	while(header_segment < heap_limit_segment) {
		HeapBlockHeader far *block = heap_header_at_segment(header_segment);
		const unsigned next_header_segment = block->next_header_segment;
		if(next_header_segment <= header_segment || next_header_segment > heap_limit_segment) {
			return 0;
		}
		if(!block->is_allocated && (next_header_segment - header_segment) >= block_paragraphs) {
			const unsigned remainder = next_header_segment - header_segment - block_paragraphs;
			if(remainder > 1u) {
				const unsigned free_tail_segment = header_segment + block_paragraphs;
				HeapBlockHeader far *free_tail = heap_header_at_segment(free_tail_segment);
				free_tail->is_allocated = 0;
				free_tail->next_header_segment = next_header_segment;
				free_tail->reserved_allocation_id = 0;
				block->next_header_segment = free_tail_segment;
			}
			block->is_allocated = 1;
			block->reserved_allocation_id = 0;
			allocated_header_segment = header_segment;
			break;
		}
		header_segment = next_header_segment;
	}

	if(!allocated_header_segment) {
		// No reusable hole fits. Carve a new block below the first header,
		// linking it to the previous first block or the exclusive sentinel.
		if((heap_first_block_segment - heap_base_segment) < block_paragraphs) {
			return 0;
		}
		allocated_header_segment = heap_first_block_segment - block_paragraphs;
		HeapBlockHeader far *block = heap_header_at_segment(allocated_header_segment);
		block->is_allocated = 1;
		block->next_header_segment = heap_first_block_segment;
		block->reserved_allocation_id = 0;
		heap_first_block_segment = allocated_header_segment;
	}
	// Keep one successful return for both paths. TC4J previously merged two
	// direct returns incorrectly, advancing a reused handle twice; see the
	// native heap note and the exact-handle reuse runtime control.
	return allocated_header_segment + 1u;
}

// Bind caller-owned paragraphs without asking DOS to allocate or free them.
// This entry does not reject rebinding; the caller owns that lifecycle.
extern "C" void TH04_PASCAL mem_assign(unsigned base_segment, unsigned paragraph_count)
{
	heap_bind_region(base_segment, paragraph_count, 0);
}

extern "C" void TH04_PASCAL mem_assign_all(void)
{
	if(!heap_base_segment) {
		heap_assign_available_dos_block();
	}
}

// Explicit DOS assignment returns zero on success and negative DOS errors.
// An already-bound heap or an empty request uses DOS insufficient-memory -8.
extern "C" int TH04_PASCAL mem_assign_dos(unsigned paragraph_count)
{
	if(heap_base_segment || paragraph_count == 0) {
		return -8;
	}
	unsigned base_segment = 0;
	const unsigned error = _dos_allocmem(paragraph_count, &base_segment);
	if(error) {
		return -(int)error;
	}
	heap_bind_region(base_segment, paragraph_count, 1);
	return 0;
}

extern "C" int TH04_PASCAL mem_unassign(void)
{
	if(!heap_base_segment) {
		return 1;
	}
	const unsigned base_segment = heap_base_segment;
	const unsigned dos_owned = heap_dos_owned;
	// Clear local ownership before freeing through DOS. A failed DOS release
	// returns zero with the heap already unbound, so this entry cannot retry.
	heap_base_segment = 0;
	heap_limit_segment = 0;
	heap_first_block_segment = 0;
	heap_dos_owned = 0;
	if(dos_owned && _dos_freemem(base_segment) != 0) {
		return 0;
	}
	return 1;
}

extern "C" void __seg *TH04_PASCAL hmem_alloc(unsigned paragraph_count)
{
	return (void __seg *)heap_allocate_paragraphs(paragraph_count);
}

extern "C" void __seg *TH04_PASCAL hmem_allocbyte(unsigned byte_count)
{
	// Round the 16-bit byte count upward to paragraphs without overflowing
	// through byte_count + 15. Zero bytes still produce a null handle.
	unsigned paragraphs = (byte_count >> 4);
	if(byte_count & 0xF) {
		paragraphs++;
	}
	return (void __seg *)heap_allocate_paragraphs(paragraphs);
}

extern "C" void TH04_PASCAL hmem_free(void __seg *data_segment_handle_arg)
{
	if(!heap_base_segment || !data_segment_handle_arg) {
		return;
	}
	const unsigned data_segment_handle = (unsigned)data_segment_handle_arg;
	if(data_segment_handle <= heap_first_block_segment || data_segment_handle > heap_limit_segment) {
		return;
	}
	// Find the exact payload segment. Interior handles and a second free of
	// an unused block are ignored. A stale handle can still alias a later
	// allocation at the same segment; there is no generation protection.
	const unsigned target_header_segment = data_segment_handle - 1u;
	unsigned previous_header_segment = 0;
	unsigned header_segment = heap_first_block_segment;
	while(header_segment < heap_limit_segment) {
		HeapBlockHeader far *block = heap_header_at_segment(header_segment);
		const unsigned next_header_segment = block->next_header_segment;
		if(next_header_segment <= header_segment || next_header_segment > heap_limit_segment) {
			return;
		}
		if(header_segment == target_header_segment) {
			if(!block->is_allocated) {
				return;
			}
			// Coalesce the higher-address free neighbor, then the lower one.
			// The chain remains in ascending segment order throughout.
			block->is_allocated = 0;
			if(next_header_segment < heap_limit_segment) {
				HeapBlockHeader far *next_header = heap_header_at_segment(next_header_segment);
				if(!next_header->is_allocated) {
					block->next_header_segment = next_header->next_header_segment;
				}
			}
			if(previous_header_segment) {
				HeapBlockHeader far *previous_header = heap_header_at_segment(previous_header_segment);
				if(!previous_header->is_allocated) {
					previous_header->next_header_segment = block->next_header_segment;
				}
			}
			// Drop the leading free prefix from the chain, returning those
			// paragraphs to the untracked lower growth interval.
			while(heap_first_block_segment < heap_limit_segment) {
				HeapBlockHeader far *first_header = heap_header_at_segment(heap_first_block_segment);
				if(first_header->is_allocated) {
					break;
				}
				heap_first_block_segment = first_header->next_header_segment;
			}
			return;
		}
		previous_header_segment = header_segment;
		header_segment = next_header_segment;
	}
}

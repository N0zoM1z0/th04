#pragma option -zCSHARED -3

#include <dos.h>

#include "src/shared/hardware/graphics.hpp"
#include "src/shared/memory/hmem.hpp"

extern "C" unsigned __cdecl graph_VramWords;
extern "C" void far pascal th04_copy_words(
    void far *destination, const void far *source, unsigned words
);

static void graph_plane_copy(
	unsigned segment, unsigned words, unsigned source_page,
	unsigned destination_page, unsigned far *scratch
)
{
	unsigned far *vram = (unsigned far *)MK_FP(segment, 0);
	outportb(0xA6, (unsigned char)source_page);
	th04_copy_words(scratch, vram, words);
	outportb(0xA6, (unsigned char)destination_page);
	th04_copy_words(vram, scratch, words);
}

extern "C" int TH04_PASCAL graph_copy_page(int to_page)
{
	const unsigned words = graph_VramWords;
	void __seg *scratch_seg = hmem_allocbyte(words * 2u);
	if(!scratch_seg) {
		return 0;
	}

	const unsigned destination_page = ((unsigned)to_page & 1u);
	const unsigned source_page = destination_page ^ 1u;
	unsigned far *scratch = (unsigned far *)MK_FP(scratch_seg, 0);
	outportb(0x7C, 0); // GRCG off before direct plane access
	graph_plane_copy(0xA800, words, source_page, destination_page, scratch);
	graph_plane_copy(0xB000, words, source_page, destination_page, scratch);
	graph_plane_copy(0xB800, words, source_page, destination_page, scratch);
	graph_plane_copy(0xE000, words, source_page, destination_page, scratch);
	hmem_free(scratch_seg);
	return 1;
}

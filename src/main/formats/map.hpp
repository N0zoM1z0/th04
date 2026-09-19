#ifndef TH04_MAIN_FORMATS_MAP_HPP
#define TH04_MAIN_FORMATS_MAP_HPP

#include "src/shared/platform/types.hpp"
#include "src/shared/formats/tile.hpp"

static const unsigned int MAP_ROWS_PER_SECTION = 5;

// On-disk .MAP structures. Tile image entries are signed 16-bit byte offsets
// into VRAM image data; using int16_t here preserves the historical
// vram_offset_t representation without importing the legacy planar header.
#pragma pack(push, 1)

struct map_header_t {
	uint16_t size;
	int16_t section_count; // unused
	int16_t unknown[2];
};

struct map_section_tiles_t {
	int16_t row[MAP_ROWS_PER_SECTION][TILES_MEMORY_X];
};

#pragma pack(pop)

typedef char th04_map_header_size_check[(sizeof(map_header_t) == 8) ? 1 : -1];
typedef char th04_map_section_size_check[
	(sizeof(map_section_tiles_t) == 320) ? 1 : -1
];

extern map_section_tiles_t __seg* map_seg;

void near map_load(void);
void near map_free(void);

#endif

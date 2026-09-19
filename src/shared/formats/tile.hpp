#ifndef TH04_SHARED_FORMATS_TILE_HPP
#define TH04_SHARED_FORMATS_TILE_HPP

// Tile metrics used by the map and .MPN file formats.
#define TILE_W 16
#define TILE_H 16

// Keep these format dimensions independent from playfield metrics.
#define TILES_X 24
#define TILES_Y 25

#define TILE_BITS_W 4
#define TILE_BITS_H 4

#if (GAME >= 4)
// TH04+ reserve 512 horizontal pixels for tile-ring storage.
#define TILES_MEMORY_X (512 / TILE_W)
#endif

#endif

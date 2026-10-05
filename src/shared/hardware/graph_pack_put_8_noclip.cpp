#pragma option -zCSHARED

#include "src/shared/hardware/graphics.hpp"
#include "src/shared/hardware/vram_planes.hpp"

// Expand a color nibble into one bit in each B/R/G/E byte. A packed pair
// contributes two adjacent pixels; four table lookups form a planar byte.
// These constants describe the format, rather than any game image data.
#define PI_COLOR_BITS(c) \
    (((c) & 1UL) | (((c) & 2UL) << 7) | \
     (((c) & 4UL) << 14) | (((c) & 8UL) << 21))
#define PI_PAIR(hi, lo) ((PI_COLOR_BITS(hi) << 1) | PI_COLOR_BITS(lo))
#define PI_PAIR_ROW(hi) \
    PI_PAIR(hi, 0), PI_PAIR(hi, 1), PI_PAIR(hi, 2), PI_PAIR(hi, 3), \
    PI_PAIR(hi, 4), PI_PAIR(hi, 5), PI_PAIR(hi, 6), PI_PAIR(hi, 7), \
    PI_PAIR(hi, 8), PI_PAIR(hi, 9), PI_PAIR(hi, 10), PI_PAIR(hi, 11), \
    PI_PAIR(hi, 12), PI_PAIR(hi, 13), PI_PAIR(hi, 14), PI_PAIR(hi, 15)
static const unsigned long pi_pair_planes[256] = {
    PI_PAIR_ROW(0), PI_PAIR_ROW(1), PI_PAIR_ROW(2), PI_PAIR_ROW(3),
    PI_PAIR_ROW(4), PI_PAIR_ROW(5), PI_PAIR_ROW(6), PI_PAIR_ROW(7),
    PI_PAIR_ROW(8), PI_PAIR_ROW(9), PI_PAIR_ROW(10), PI_PAIR_ROW(11),
    PI_PAIR_ROW(12), PI_PAIR_ROW(13), PI_PAIR_ROW(14), PI_PAIR_ROW(15)
};
#undef PI_PAIR_ROW
#undef PI_PAIR
#undef PI_COLOR_BITS

// The cutscene uses the otherwise invisible row 400 as an EGC source row.
// graph_pack_put_8() clips that row, so unpack the 4-bit PI pixels directly
// into the four VRAM planes selected by graph_accesspage().
extern "C" void far pascal graph_pack_put_8_noclip(
    screen_x_t left, screen_y_t top, const void far *linepat, pixel_t len
)
{
    int byte_x = (left >> BYTE_BITS);
    int count = (len >> BYTE_BITS);
    if((count <= 0) || (byte_x >= ROW_SIZE)) {
        return;
    }

    const unsigned char far *src = reinterpret_cast<const unsigned char far *>(linepat);
    if(byte_x < 0) {
        int skip = -byte_x;
        if(skip >= count) {
            return;
        }
        src += (skip * 4);
        count -= skip;
        byte_x = 0;
    }
    if((byte_x + count) > ROW_SIZE) {
        count = (ROW_SIZE - byte_x);
    }

    unsigned int destination = ((top << 6) + (top << 4) + byte_x);
    for(int x = 0; x < count; x++) {
        unsigned long planes = (pi_pair_planes[src[0]] << 6) |
            (pi_pair_planes[src[1]] << 4) |
            (pi_pair_planes[src[2]] << 2) | pi_pair_planes[src[3]];
        VRAM_PLANE_B[destination + x] = (unsigned char)planes;
        VRAM_PLANE_R[destination + x] = (unsigned char)(planes >> 8);
        VRAM_PLANE_G[destination + x] = (unsigned char)(planes >> 16);
        VRAM_PLANE_E[destination + x] = (unsigned char)(planes >> 24);
        src += 4;
    }
}

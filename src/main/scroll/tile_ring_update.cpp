#pragma option -zCEND_TEXT -zPmain_01

#include <dos.h>
#include <mem.h>

// END_TEXT scroll/tile-ring helper at MAIN.EXE load 0xB835. Address-style
// names mark BSS state whose wider ownership is still unresolved.
extern "C" unsigned char byte_250FE;
extern "C" unsigned char byte_25104;
extern "C" unsigned int word_25100;

extern unsigned char scroll_speed;
extern unsigned int scroll_line;
extern unsigned char scroll_active;
extern signed char tile_row_in_section;
extern unsigned int std_map_section_id;
extern unsigned int std_scroll_speed;
extern unsigned char __seg *std_seg;
extern unsigned char __seg *map_seg;
extern const unsigned int TILE_SECTION_OFFSETS[32];
extern unsigned int tile_ring[][32];

extern void near egc_start_copy_noframe();
extern "C" void near sub_BAEE();
extern void far egc_off();

void near scroll_tile_ring_update()
{
    unsigned char previous_copy_request;
    if((byte_25104 == 0) && (byte_250FE == 0)) {
        return;
    }
    if(scroll_speed == 0) {
        return;
    }

    unsigned int row = (scroll_line >> 4);
    if(row != word_25100) {
        word_25100 = row;
        if((--tile_row_in_section) < 0) {
            tile_row_in_section = 4;
            std_map_section_id++;
            std_scroll_speed++;
            if((scroll_speed = std_seg[std_scroll_speed]) == 0) {
                scroll_line = 0;
                byte_250FE = 0;
                byte_25104 = 0;
                return;
            }
        }

        unsigned int source_offset =
            ((unsigned int)(unsigned char)tile_row_in_section * 64)
            + TILE_SECTION_OFFSETS[std_seg[std_map_section_id]];
        __memcpy__(
            &tile_ring[row][0],
            MK_FP((unsigned int)map_seg, source_offset),
            48
        );
    }

    previous_copy_request = byte_250FE;
    byte_250FE = byte_25104;
    byte_25104 += previous_copy_request;
    if(scroll_active == 0) {
        byte_25104 = 0;
        return;
    }
    egc_start_copy_noframe();
    sub_BAEE();
    byte_25104 = 0;
    egc_off();
}

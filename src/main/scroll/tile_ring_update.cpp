#pragma option -zCEND_TEXT -zPmain_01

#include <dos.h>
#include <mem.h>

#define X86_SIGN_FLAG_SET (_FLAGS & 0x80)

// Preserve the historical external names in OMF while exposing the meanings
// already used by native stage initialization.
extern "C" unsigned char byte_250FE;
#define scroll_row_advance_previous byte_250FE
extern "C" unsigned char byte_25104;
#define scroll_row_advance_current byte_25104
extern "C" unsigned int word_25100;
#define tile_ring_scroll_row_previous word_25100

extern unsigned char scroll_speed;
extern unsigned int scroll_line;
extern unsigned char scroll_active;
extern signed char tile_row_in_section;
extern unsigned int std_map_section_id;
#define std_map_section_cursor std_map_section_id
extern unsigned int std_scroll_speed;
#define std_scroll_speed_cursor std_scroll_speed
extern unsigned char __seg *std_seg;
extern unsigned char __seg *map_seg;
extern const unsigned int TILE_SECTION_OFFSETS[32];
extern unsigned int tile_ring[][32];

extern void near egc_start_copy_noframe();
extern "C" void near sub_BAEE();
#define tile_ring_copy_scrolled_rows sub_BAEE
extern "C" void pascal far egc_off(void);

void near scroll_tile_ring_update()
{
    unsigned char previous_row_advance;

    // A request survives for one additional frame. If neither slot contains
    // an advance, no map row or graphics byte can become newly visible.
    if(
        (scroll_row_advance_current == 0) &&
        (scroll_row_advance_previous == 0)
    ) {
        return;
    }
    // A zero in the STD speed stream is the stage-scroll terminator. Do not
    // consume queued rows after that sentinel has been installed.
    if(scroll_speed == 0) {
        return;
    }

    // One ring entry represents one 16-pixel tile row. Refresh its 24 visible
    // tile words only when the wrapped display origin enters a different row.
    _AX = scroll_line;
    _AX >>= 4;
    if(_AX != tile_ring_scroll_row_previous) {
        tile_ring_scroll_row_previous = _AX;

        // ES addresses the loaded STD. tile_row_in_section counts backward
        // through a five-row map section as the playfield scrolls upward.
        _BX = (unsigned int)std_seg;
        _ES = _BX;
        tile_row_in_section--;
        if(X86_SIGN_FLAG_SET) {
            // Underflow advances both parallel STD byte streams: the next map
            // section ID and the speed applied while revealing that section.
            tile_row_in_section = 4;
            std_map_section_cursor++;
            std_scroll_speed_cursor++;

            _BX = std_scroll_speed_cursor;
            _DL = *reinterpret_cast<unsigned char __es *>(_BX);
            scroll_speed = _DL;
            if(_DL == 0) {
                // End of the speed stream resets the wrapped origin and drops
                // both halves of the pending two-frame copy request.
                scroll_line = 0;
                scroll_row_advance_previous = 0;
                scroll_row_advance_current = 0;
                return;
            }
        }

        // Destination: one of 25 ring rows, 32 words (64 bytes) apart.
        _AX <<= 6;
        _AX += (unsigned int)&tile_ring[0][0];
        asm { mov di, ax; }

        // Source row within a five-row, 64-byte-per-row map section.
        asm { xor ax, ax; }
        _AL = tile_row_in_section;
        _AX <<= 6;

        // The STD section-order byte selects a word offset into MAP data.
        _BX = std_map_section_cursor;
        _BL = *reinterpret_cast<unsigned char __es *>(_BX);
        asm {
            xor bh, bh
            add bl, bl
        }
        _BX = *reinterpret_cast<const unsigned int *>(
            reinterpret_cast<const unsigned char *>(TILE_SECTION_OFFSETS) + _BX
        );
        // DI points into DGROUP's ring and SI into map_seg. Copy the 24 tiles
        // visible across the 384-pixel playfield; the ring's remaining eight
        // columns are outside this row update.
        asm {
            mov si, ax
            add si, bx
            push ds
            pop es
            push ds
            mov ax, map_seg
            mov ds, ax
            mov cx, 24
            rep movsw
            pop ds
        }
    }

    // Promote this frame's advance for the next hardware-origin update, then
    // combine it with the preceding advance for the EGC row copier. The copier
    // reads scroll_row_advance_current directly.
    previous_row_advance = scroll_row_advance_previous;
    scroll_row_advance_previous = scroll_row_advance_current;
    scroll_row_advance_current += previous_row_advance;
    if(scroll_active == 0) {
        // Keep the ring and request handoff current while Bomb effects suspend
        // display scrolling, but do not touch graphics RAM.
        scroll_row_advance_current = 0;
        return;
    }
    egc_start_copy_noframe();
    tile_ring_copy_scrolled_rows();
    scroll_row_advance_current = 0;
    egc_off();
}

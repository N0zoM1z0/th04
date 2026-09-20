#pragma option -zCEND_TEXT -zPmain_01

#include <dos.h>
#include <mem.h>

#define FLAGS_SIGN (_FLAGS & 0x80)

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

    _AX = scroll_line;
    _AX >>= 4;
    if(_AX != word_25100) {
        word_25100 = _AX;

        _BX = (unsigned int)std_seg;
        _ES = _BX;
        tile_row_in_section--;
        if(FLAGS_SIGN) {
            tile_row_in_section = 4;
            std_map_section_id++;
            std_scroll_speed++;

            _BX = std_scroll_speed;
            _DL = *reinterpret_cast<unsigned char __es *>(_BX);
            scroll_speed = _DL;
            if(_DL == 0) {
                scroll_line = 0;
                byte_250FE = 0;
                byte_25104 = 0;
                return;
            }
        }

        _AX <<= 6;
        _AX += (unsigned int)&tile_ring[0][0];
        asm { mov di, ax; }

        asm { xor ax, ax; }
        _AL = tile_row_in_section;
        _AX <<= 6;

        _BX = std_map_section_id;
        _BL = *reinterpret_cast<unsigned char __es *>(_BX);
        asm {
            xor bh, bh
            add bl, bl
        }
        _BX = *reinterpret_cast<const unsigned int *>(
            reinterpret_cast<const unsigned char *>(TILE_SECTION_OFFSETS) + _BX
        );
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

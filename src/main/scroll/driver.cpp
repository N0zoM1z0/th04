#pragma option -zCMAI_TEXT -zPmain_01

#define X86_SIGN_FLAG_SET (_FLAGS & 0x80)

// MAI_TEXT scroll driver at MAIN.EXE load 0xCCD6. The historical linker names
// remain below because exact replay links this owner against pinned surrounding
// objects. Source expressions use the semantic aliases shared with native
// initialization; all aliases still resolve to the same bytes.
extern unsigned char page_back;
extern unsigned int scroll_line_on_page[2];
extern int scroll_line;
extern "C" unsigned char byte_250FE;
#define scroll_row_advance_previous byte_250FE
extern unsigned char scroll_active;
extern unsigned int scroll_last_delta;
extern unsigned char scroll_subpixel_line;
extern unsigned char scroll_speed;
extern "C" unsigned char byte_25104;
#define scroll_row_advance_current byte_25104

extern "C" void pascal far graph_scrollup(unsigned line);
extern void near scroll_tile_ring_update(void);

void near scroll_driver()
{
    // Each VRAM page remembers the display origin last prepared for it. The
    // previous frame's row advance gates the hardware origin update: the tile
    // copier below has already supplied the rows that this origin will reveal.
    scroll_line_on_page[page_back] = scroll_line;
    if(scroll_row_advance_previous && scroll_active) {
        graph_scrollup(static_cast<unsigned>(scroll_line));
    }

    // scroll_subpixel_line is the Q12.4 fractional accumulator. Crossing 16
    // yields an integer 0..15 pixel advance; keep the remainder for the next
    // frame and publish the consumed distance in both pixel and subpixel units.
    scroll_last_delta = 0;
    if((scroll_subpixel_line = (scroll_subpixel_line + scroll_speed)) >= 16) {
        // Keep the quotient in AX. The signed cast tells TC4J that AX is the
        // complete 16-bit RHS, avoiding both a byte-local spill and an
        // unnecessary second zero-extension of AL.
        _AH = 0;
        _AX >>= 4;
        scroll_line -= static_cast<int>(_AX);
        if(X86_SIGN_FLAG_SET) {
            // PC-98 VRAM is 400 scanlines tall, so upward motion wraps the
            // display origin from line 0 back to line 399.
            scroll_line += 400;
        }
        scroll_row_advance_current = _AL;
        scroll_subpixel_line &= 15;
        _AX <<= 4;
        scroll_last_delta = _AX;
    }

    // This call also consumes a request left by the previous frame. It must
    // run on zero-advance frames so that the two-frame handoff can complete.
    scroll_tile_ring_update();
}

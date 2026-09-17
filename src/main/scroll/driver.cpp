#pragma option -zCMAI_TEXT -zPmain_01

// MAI_TEXT scroll driver at MAIN.EXE load 0xCCD6. The two unresolved BSS
// flags keep their target-address names until their wider ownership is known.
extern unsigned char page_back;
extern unsigned int scroll_line_on_page[2];
extern int scroll_line;
extern "C" unsigned char byte_250FE;
extern unsigned char scroll_active;
extern unsigned int scroll_last_delta;
extern unsigned char scroll_subpixel_line;
extern unsigned char scroll_speed;
extern "C" unsigned char byte_25104;

extern void pascal far graph_scrollup(int line);
extern "C" void near sub_B835();

void near scroll_driver()
{
    scroll_line_on_page[page_back] = scroll_line;
    if(byte_250FE && scroll_active) {
        graph_scrollup(scroll_line);
    }

    scroll_last_delta = 0;
    if((scroll_subpixel_line = (scroll_subpixel_line + scroll_speed)) >= 16) {
        unsigned char lines = ((unsigned int)scroll_subpixel_line >> 4);
        if((scroll_line -= lines) < 0) {
            scroll_line += 400;
        }
        byte_25104 = lines;
        scroll_subpixel_line &= 15;
        scroll_last_delta = (lines << 4);
    }
    sub_B835();
}

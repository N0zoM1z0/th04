#include "src/shared/hardware/graphics.hpp"

void near nopoly_B_put(void);
void near polygons_update_and_render(void);
void far pascal frame_delay_2(int frames);
extern unsigned char music_page_accessed;

#pragma codeseg OP_MUSIC_TEXT op_music_01
#include "src/op/music/music_update_render_and_flip.inl"
#pragma codeseg

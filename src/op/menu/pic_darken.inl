void pascal near pic_darken(playchar_t playchar)
{
	vram_offset_t vo;
	if(playchar == 0) {
		vo = ((PLAYCHAR_TOP * ROW_SIZE) + (REIMU_LEFT / BYTE_DOTS));
	} else {
		vo = ((PLAYCHAR_TOP * ROW_SIZE) + (MARISA_LEFT / BYTE_DOTS));
	}

	vram_byte_amount_t x;
	pixel_t y;
	grcg_setcolor(GC_RMW, 1);
	dots32_t pattern = 0xAAAAAAAAUL;

	y = 0;
	while(y < PIC_H) {
		pattern = ((y & 1) == 0) ? 0xAAAAAAAAUL : 0x55555555UL;

		x = 0;
		while(x < (PIC_W / BYTE_DOTS)) {
			*reinterpret_cast<dots32_t far *>(VRAM_PLANE_B + vo) = pattern;
			x += static_cast<vram_byte_amount_t>(sizeof(pattern));
			vo += static_cast<vram_offset_t>(sizeof(pattern));
		}
		y++;
		vo += (ROW_SIZE - (PIC_W / BYTE_DOTS));
	}
	outportb(0x7C, 0);
}

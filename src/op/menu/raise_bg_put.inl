void near pascal raise_bg_put(playchar_t playchar_lowered)
{
	vram_byte_amount_t x;
	pixel_t y;
	vram_offset_t vo_row;
	dots8_t far *playchar_bg;
	vram_offset_t vo;

	if(playchar_lowered == PLAYCHAR_REIMU) {
		vo_row = raise(vram_offset_shift(REIMU_LEFT, PLAYCHAR_TOP));
		playchar_bg = raise_bg[PLAYCHAR_REIMU];
	} else {
		vo_row = raise(vram_offset_shift(MARISA_LEFT, PLAYCHAR_TOP));
		playchar_bg = raise_bg[PLAYCHAR_MARISA];
	}

	// Top edge
	for(y = 0; y < RAISE_H; y++, vo_row += ROW_SIZE) {
		x = 0;
		vo = vo_row;
		while(x < (PIC_W / BYTE_DOTS)) {
			raise_bg_put_and_advance_planar(vo, playchar_bg);
			x++;
			vo++;
		}
	}

	// Left edge
	for(y = 0; y < PIC_H; y++, vo_row += ROW_SIZE) {
		raise_bg_put_and_advance_planar(vo_row, playchar_bg);
	}
}

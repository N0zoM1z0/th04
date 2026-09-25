void near raise_bg_allocate_and_snap(void)
{
	size_t raise_bg_p;
	vram_offset_t vo_reimu_row;
	pixel_t y;
	vram_byte_amount_t x;
	vram_offset_t vo_reimu;
	vram_offset_t vo_marisa_row;
	vram_offset_t vo_marisa;

	raise_bg[PLAYCHAR_REIMU] = HMem<dots8_t>::alloc(RAISE_BG_SIZE);
	raise_bg[PLAYCHAR_MARISA] = HMem<dots8_t>::alloc(RAISE_BG_SIZE);

	vo_reimu_row  = raise(vram_offset_shift(REIMU_LEFT,  PLAYCHAR_TOP));
	vo_marisa_row = raise(vram_offset_shift(MARISA_LEFT, PLAYCHAR_TOP));

	// Top edge
	y = 0;
	raise_bg_p = 0;
	while(y < RAISE_H) {
		x = 0;
		vo_reimu = vo_reimu_row;
		vo_marisa = vo_marisa_row;
		while(x < (PIC_W / BYTE_DOTS)) {
			raise_bg_snap_and_advance_planar(raise_bg_p, vo_reimu, vo_marisa);
			x++;
			vo_reimu++;
			vo_marisa++;
		}
		y++;
		vo_reimu_row  += ROW_SIZE;
		vo_marisa_row += ROW_SIZE;
	}

	// Left edge
	y = 0;
	while(y < PIC_H) {
		raise_bg_snap_and_advance_planar(
			raise_bg_p, vo_reimu_row, vo_marisa_row
		);
		y++;
		vo_reimu_row  += ROW_SIZE;
		vo_marisa_row += ROW_SIZE;
	}
}

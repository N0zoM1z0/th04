void near playfield_checkerboard_grcg_tdw_update_and_render(void)
{
	#define loops_and_vo_x	_BX
	#define loops         	_BH
	#define vo_x          	_BL

	// Not vram_offset_t, as it's relative to the custom segments calculated
	// from [seg_bottom].
	#define vram_off static_cast<int16_t>(_DI)

	// Same signedness issue as with [seg_bottom].
	#define vram_seg static_cast<int16_t>(_DX)

	grcg_setcolor_direct_constant(0);
	loops_and_vo_x = checkerboard.u1.both;

	// Bottom row
	while(1) {
		vram_seg = checkerboard.seg_bottom;
		vram_off = loops_and_vo_x;
		vram_off &= 0xFF; // Isolate [vo_x], ignoring the loop count
		vram_off += checkerboard.off_bottom;
		goto put;

		// Top row
		do {
			vram_seg = grcg_segment(0, PLAYFIELD_TOP);
			vram_off = loops_and_vo_x;
			vram_off &= 0xFF; // Isolate [vo_x], ignoring the loop count
			vram_off += checkerboard.off_top;
			goto put;

			// Fully visible, regular rows within the playfield
			do {
				vram_off = loops_and_vo_x;
				vram_off &= 0xFF; // Isolate [vo_x], ignoring the loop count
				vram_off += ((CHECKERBOARD_H - 1) * ROW_SIZE);

			put:
				_ES = vram_seg;
				do {
					_CX = ((PLAYFIELD_W / CHECKERBOARD_W) / 2);

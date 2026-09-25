void pascal near pic_put_both_masked(
	screen_x_t left, vram_y_t top, int quarter, int mask_id
)
{
	enum {
		TEMP_ROW = RES_Y,
	};

	vram_word_amount_t vram_word;
	vram_offset_t vo_temp;
	pi_buffer_p_t row_p;

	pi_buffer_p_init_quarter(row_p, CUTSCENE_PIC_SLOT, quarter);

	// ZUN bloat: See the call site.
	graph_showpage(1);
	vram_offset_t vo = vram_offset_shift(left, top);
	graph_accesspage(0);
	for(pixel_t y = 0; y < CUTSCENE_PIC_H; y++) {
		// This actually is much faster than clearing the masked pixels using
		// the GRCG and doing an unaccelerated 4-plane VRAM OR. See the
		// `Research/blitperf/xfade` example for a benchmark.
		graph_pack_put_8_noclip(0, TEMP_ROW, row_p, CUTSCENE_PIC_W);
		egc_start_copy();
		egc_setup_copy_masked(PI_MASKS[mask_id][y % PI_MASK_COUNT]);
		vo_temp = vram_offset_shift(0, TEMP_ROW);
		vram_word = 0;
		while(vram_word < (CUTSCENE_PIC_W / EGC_REGISTER_DOTS)) {
			egc_chunk(vo) = egc_chunk(vo_temp);
			vram_word++;
			vo += EGC_REGISTER_SIZE;
			vo_temp += EGC_REGISTER_SIZE;
		}
		egc_off();

		vo += (ROW_SIZE - CUTSCENE_PIC_VRAM_W);
		pi_buffer_p_offset(row_p, PI_W, 0);
		pi_buffer_p_normalize(row_p);
	}
	graph_showpage(0);
	pic_copy_to_other(left, top);
}

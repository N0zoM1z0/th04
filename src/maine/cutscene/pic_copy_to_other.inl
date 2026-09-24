void pascal near pic_copy_to_other(screen_x_t left, vram_y_t top)
{
	vram_offset_t vo = (
		(left >> BYTE_BITS) +
		(top << 6) +
		(top << 4)
	);
	pixel_t y;
	vram_byte_amount_t vram_x;

	egc_start_copy();

	y = 0;
	while(y < CUTSCENE_PIC_H) {
		vram_x = 0;
		while(vram_x < CUTSCENE_PIC_VRAM_W) {
			egc_temp_t tmp;

			graph_accesspage(0);
			tmp = *reinterpret_cast<egc_temp_t far *>(VRAM_PLANE_B + vo);
			graph_accesspage(1);
			*reinterpret_cast<egc_temp_t far *>(VRAM_PLANE_B + vo) = tmp;

			vram_x += static_cast<vram_byte_amount_t>(sizeof(egc_temp_t));
			vo += static_cast<vram_offset_t>(sizeof(egc_temp_t));
		}
		y++;
		vo += (ROW_SIZE - CUTSCENE_PIC_VRAM_W);
	}
	egc_off();
	graph_accesspage(0);
}

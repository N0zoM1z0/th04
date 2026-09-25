void near box_bg_allocate_and_snap(void)
{
	box_bg_free();
	graph_accesspage(0);
	box_bg = HMem< Planar<dots16_t> >::alloc(
		(BOX_VRAM_W * BOX_H) / sizeof(dots16_t)
	);

	size_t p;
	vram_y_t src_y;
	screen_x_t src_x;
	pixel_t dst_y;
	vram_byte_amount_t dst_byte;
	vram_offset_t vo;
	p = 0;
	src_y = BOX_TOP;
	dst_y = 0;
	while(dst_y < BOX_H) {
		src_x = BOX_LEFT;
		dst_byte = 0;
		while(dst_byte < BOX_VRAM_W) {
			vo = ((src_x >> BYTE_BITS) + (src_y << 6) + (src_y << 4));
			(&box_bg->B)[p++] = *reinterpret_cast<dots16_t far *>(VRAM_PLANE_B + vo);
			(&box_bg->B)[p++] = *reinterpret_cast<dots16_t far *>(VRAM_PLANE_R + vo);
			(&box_bg->B)[p++] = *reinterpret_cast<dots16_t far *>(VRAM_PLANE_G + vo);
			(&box_bg->B)[p++] = *reinterpret_cast<dots16_t far *>(VRAM_PLANE_E + vo);
			dst_byte += static_cast<vram_byte_amount_t>(sizeof(dots16_t));
			src_x += 16;
		}
		dst_y++;
		src_y++;
	}
}

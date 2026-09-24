void pascal near box_1_to_0_masked(box_mask_t mask)
{
	for(screen_y_t y = BOX_TOP; y < BOX_BOTTOM; y++) {
		outport(EGC_READPLANEREG, 0x00FF);
		outport(
			EGC_MODE_ROP_REG,
			(EGC_COMPAREREAD | EGC_WS_PATREG | EGC_RL_MEMREAD)
		);
		outport(EGC_BITLENGTHREG, (EGC_REGISTER_DOTS - 1));
		outport(EGC_MASKREG, BOX_MASKS[mask][y & 3]);

		vram_offset_t vo = ((y << 6) + (y << 4) + (BOX_LEFT / BYTE_DOTS));
		pixel_t x = 0;
		while(x < BOX_W) {
			graph_accesspage(1);
			egc_temp_t tmp = *reinterpret_cast<egc_temp_t far *>(
				VRAM_PLANE_B + vo
			);
			graph_accesspage(0);
			*reinterpret_cast<egc_temp_t far *>(VRAM_PLANE_B + vo) = tmp;
			x += EGC_REGISTER_DOTS;
			vo += EGC_REGISTER_SIZE;
		}
	}
}

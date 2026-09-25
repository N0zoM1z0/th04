void pascal near score_rect_copy(int left, int top, int w, int h)
{
	int x;
	int y;
	vram_offset_t vo;
	dots16_t dots;
	register vram_offset_t vo_r;
	register int word_w = w;
	score_egc_start_copy();
	vo = ((left >> 3) + (top << 6) + (top << 4));
	word_w /= 16;
	for(y = 0; y < h; y++, vo += ROW_SIZE) {
		x = 0;
		vo_r = vo;
		for(; x < word_w; x++, vo_r += 2) {
			_DX = 0xA6;
			outportb(_DX, 1);
			dots = *reinterpret_cast<dots16_t far *>(VRAM_PLANE_B + vo_r);
			outportb(_DX, 0);
			*reinterpret_cast<dots16_t far *>(VRAM_PLANE_B + vo_r) = dots;
		}
	}
	egc_off();
}

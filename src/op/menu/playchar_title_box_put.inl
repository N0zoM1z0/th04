void pascal near playchar_title_box_put(int playchar)
{
	screen_x_t left;
	vram_y_t top;

	playchar_title_left_for(left, playchar);
	top = PLAYCHAR_TITLE_TOP;

	grcg_setcolor(GC_RMW, COL_SHADOW);
	grcg_round_boxfill(
		(left + SHADOW_DISTANCE),
		(top + SHADOW_DISTANCE),
		(left + SHADOW_DISTANCE + PLAYCHAR_TITLE_W),
		(top + SHADOW_DISTANCE + (BOX_ROUND * 2) + PLAYCHAR_TITLE_H),
		BOX_ROUND
	);

	grcg_setcolor(GC_RMW, COL_BOX);
	grcg_round_boxfill(
		left,
		top,
		(left + PLAYCHAR_TITLE_W),
		(top + (BOX_ROUND * 2) + PLAYCHAR_TITLE_H),
		BOX_ROUND
	);

	outportb(0x7C, 0);
}

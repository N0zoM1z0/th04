void near shottype_title_box_put(void)
{
	vram_y_t top = SHOTTYPE_BOX_TOP;
	screen_x_t left = SHOTTYPE_TITLE_LEFT;

	#define box_top(top, i) \
		(top + (i * (GLYPH_H + (SHOTTYPE_BOX_PADDING_Y * 2))))

	#define put(func, left, top, w) \
		func(left, top, w, (GLYPH_H - 1), SHOTTYPE_BOX_PADDING_Y)

	grcg_setcolor(GC_RMW, COL_SHADOW);
	put(box_shadow_put, left, box_top(top, 0), (SHOTTYPE_TITLE_W - 1));
	put(box_shadow_put, left, box_top(top, 1), (SHOTTYPE_TITLE_W - 1));
	put(box_shadow_put, SHOTTYPE_CHOOSE_LEFT, top, (SHOTTYPE_CHOOSE_W - 1));

	grcg_setcolor(GC_RMW, COL_BOX);
	put(box_put, left, box_top(top, 0), SHOTTYPE_TITLE_W);
	put(box_put, left, box_top(top, 1), SHOTTYPE_TITLE_W);
	put(box_put, SHOTTYPE_CHOOSE_LEFT, top, (SHOTTYPE_CHOOSE_W - 1));

	grcg_off();

	graph_putsa_fx(
		(SHOTTYPE_CHOOSE_LEFT + SHOTTYPE_CHOOSE_PADDING_LEFT),
		(top + SHOTTYPE_BOX_PADDING_Y),
		COL_NOT_SELECTED,
		SHOTTYPE_CHOOSE
	);

	#undef put
	#undef box_top
}

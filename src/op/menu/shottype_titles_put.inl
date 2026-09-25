void near pascal shottype_titles_put(int sel)
{
	vram_y_t top;
	screen_x_t left;
	int rank = ((resident->stage == STAGE_EXTRA) ? RANK_EXTRA : resident->rank);
	uint8_t clearflag;

	#define put(left, top, clearflag, rank, col) \
		if(cleared_with[playchar_menu_sel][rank] & clearflag) { \
			graph_putsa_fx_func = FX_WEIGHT_NORMAL; \
			graph_putsa_fx( \
				(left - GLYPH_HALF_W), \
				(top + SHOTTYPE_BOX_PADDING_Y), \
				COL_SELECTED, \
				SHOTTYPE_CLEARED \
			); \
			graph_putsa_fx_func = FX_WEIGHT_BOLD; \
		} \
		graph_putsa_fx( \
			(left + GLYPH_HALF_W), \
			(top + SHOTTYPE_BOX_PADDING_Y), \
			col, \
			SHOTTYPE_TITLE[playchar_menu_sel][sel] \
		);

	// Selected shot type
	shottype_title_top_and_clearflag_for(top, clearflag, sel);
	left = SHOTTYPE_TITLE_LEFT;
	put(left, top, clearflag, rank, COL_SELECTED);

	// Other shot type
	sel = (SHOTTYPE_B - sel);
	shottype_title_top_and_clearflag_for(top, clearflag, sel);
	put(left, top, clearflag, rank, COL_NOT_SELECTED);

	#undef put
}

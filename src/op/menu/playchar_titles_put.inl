void near pascal playchar_titles_put(int sel)
{
	screen_x_t left;
	vram_y_t top;

	#define title_left_for(left_, playchar_) 		switch(playchar_) { 		case PLAYCHAR_REIMU:  left_ = (REIMU_LEFT + 32); break; 		case PLAYCHAR_MARISA: left_ = (MARISA_LEFT + 32); break; 		}

	#define put_titles(left_, top_, col_) 		graph_putsa_fx( 			(left_ + BOX_ROUND), (top_ + BOX_ROUND), col_, PLAYCHAR_TITLE[sel][0] 		); 		graph_putsa_fx( 			(left_ + BOX_ROUND), 			((top_ + BOX_ROUND) + (GLYPH_H * 2)), 			col_, 			PLAYCHAR_TITLE[sel][1] 		)

	title_left_for(left, sel);
	top = PLAYCHAR_TITLE_TOP;
	put_titles(left, top, COL_SELECTED);

	sel = (PLAYCHAR_MARISA - sel);
	title_left_for(left, sel);
	put_titles(left, top, COL_NOT_SELECTED);

	#undef put_titles
	#undef title_left_for
}

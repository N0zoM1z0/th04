void near cursor_advance_and_animate(void)
{
	cursor.x += GLYPH_FULL_W;
	if(cursor.x >= BOX_RIGHT) {
		cursor.y += GLYPH_H;
		cursor.x = (BOX_LEFT + NAME_W);

		if(cursor.y >= BOX_BOTTOM) {
			box_1_to_0_animate();

			if(!fast_forward) {
				input_wait_for_change(0);
			}

			cursor.x = BOX_LEFT;
			cursor.y = BOX_TOP;

			graph_accesspage(1);
			box_bg_put();
			graph_accesspage(0);
			box_bg_put();
		}
	}
}

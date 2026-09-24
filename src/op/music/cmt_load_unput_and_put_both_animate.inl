void pascal near cmt_load_unput_and_put_both_animate(int track)
{
	if(cmt_shown_initial) {
		cmt_unput_both_animate();
	}
	cmt_load(track);

	nopoly_B_put();
	bgimage_put_rect_16(
		CMT_TITLE_LEFT,
		CMT_TITLE_TOP,
		(RES_X - CMT_TITLE_LEFT),
		(CMT_LINES * GLYPH_H)
	);

	if(cmt_shown_initial) {
		cmt_fadein_both_animate();
	} else {
		cmt_shown_initial = true;
		cmt_put();
		music_update_render_and_flip();
		cmt_put();
	}

	nopoly_B_put();
}

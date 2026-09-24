void near cmt_fadein_both_animate(void)
{
	int func;
	for(func = 4; func < 8; func++) {
		graph_putsa_fx_func = func;
		cmt_put();
		music_update_render_and_flip();
		cmt_put();
		music_update_render_and_flip();
	}
	graph_putsa_fx_func = 2;
	cmt_put();
	music_update_render_and_flip();
	cmt_put();
}

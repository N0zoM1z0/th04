void near cmt_unput_both_animate(void)
{
	graph_putsa_fx_func = 2;
	bgimage_put_rect_16(320, 64, 320, 320);
	music_update_render_and_flip();
	bgimage_put_rect_16(320, 64, 320, 320);
}

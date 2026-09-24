void near music_update_render_and_flip(void)
{
	nopoly_B_put();
	grcg_setcolor((GC_RMW | GC_B), 0xF);
	polygons_update_and_render();
	outportb(0x7C, 0);

	graph_showpage(music_page_accessed);
	music_page_accessed = (1 - music_page_accessed);
	graph_accesspage(music_page_accessed);
	frame_delay_2(1);
}

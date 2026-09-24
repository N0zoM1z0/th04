void near playchar_menu_put_initial(void)
{
	palette_settone(0);
	pi_load(0, "slb1.pi");
	graph_accesspage(1);
	graph_showpage(0);
	pi_palette_apply(0);
	pi_put_8(0, 0, 0);
	raise_bg_allocate_and_snap();
	playchar_title_box_put(0);
	playchar_title_box_put(1);
	pic_put();
	graph_copy_page(0);
	palette_black_in(1);
}

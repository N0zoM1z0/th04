void near setup_menu(void)
{
	palette_settone(0);
	super_entry_bfnt("mswin.bft");
	graph_accesspage(1);
	pi_fullres_load_palette_apply_put_free(0, "ms.pi");
	graph_copy_page(0);
	palette_black_in(1);

	setup_bgm_menu();
	frame_delay(1);

	graph_copy_page(0);
	setup_se_menu();
	palette_black_out(1);

	super_free();
}

void near verdict_animate(void)
{
	PaletteTone = 0;
	palette_show();
	graph_accesspage(1);
	pi_load(0, aUde_pi);
	pi_palette_apply(0);
	pi_put_8(0, 0, 0);
	pi_free(0);
	graph_copy_page(0);
	palette_black_in(4);
	sub_BB81();
}

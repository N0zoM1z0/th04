void pascal near staffroll_dissolve_out(screen_x_t base_left, screen_y_t base_top)
{
	register int distance;
	register screen_x_t left = base_left;
	distance = 63;
	int page = 0;
	graph_accesspage(0);
	graph_showpage(1);
	while(distance > 0) {
		staffroll_bgimage_expand_put(
			left, base_top,
			cdg_slots[cdg_slot].pixel_w,
			cdg_slots[cdg_slot].pixel_h,
			(distance + 1)
		);
		distance--;
		radial_angle += 8;
		dissolve_put_func(left, base_top, distance);
		while(vsync_Count1 < 2) { }
		vsync_Count1 = 0;
		graph_showpage(page);
		page = (1 - page);
		graph_accesspage(page);
	}
	graph_copy_page(page);
}

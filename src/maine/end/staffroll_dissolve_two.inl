void pascal near staffroll_dissolve_two(
	screen_x_t base_left_1, screen_y_t base_top_1,
	screen_x_t base_left_2, screen_y_t base_top_2
)
{
	register int distance;
	register screen_x_t left_1 = base_left_1;
	distance = 0;
	int page = 0;
	graph_accesspage(0);
	graph_showpage(1);
	while(true) {
		staffroll_bgimage_expand_put(
			left_1, base_top_1,
			cdg_slots[2].pixel_w,
			cdg_slots[2].pixel_h,
			distance
		);
		staffroll_bgimage_expand_put(
			base_left_2, base_top_2,
			cdg_slots[0].pixel_w,
			cdg_slots[0].pixel_h,
			distance
		);
		distance++;
		radial_angle -= 8;
		if(distance >= 64) {
			break;
		}
		cdg_slot = 2;
		dissolve_put_func(left_1, base_top_1, distance);
		cdg_slot = 0;
		dissolve_put_func(base_left_2, base_top_2, distance);
		while(vsync_Count1 < 2) { }
		vsync_Count1 = 0;
		graph_showpage(page);
		page = (1 - page);
		graph_accesspage(page);
	}
	graph_copy_page(1 - page);
}

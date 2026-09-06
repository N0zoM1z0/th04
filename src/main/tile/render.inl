void near tiles_invalidate_all(void)
{
	tiles_invalidate_set_all(true);
}

#pragma option -k.

void pascal near tiles_render(void)
{
	overlay_titles_invalidate();
	player_invalidate();
	shots_invalidate();
	enemies_invalidate();
	bullets_and_gather_invalidate();
	items_invalidate();
	sparks_invalidate();
	pointnums_invalidate();
	midboss_invalidate();
	stage_invalidate();

	tiles_redraw_invalidated();
}

static void pascal near tiles_render_all_timed(void)
{
	tiles_render_all();
	render_all_time--;
	if(render_all_time == 0) {
		bg_render_not_bombing = tiles_render;
	}
}

void tiles_activate(void)
{
	bg_render_not_bombing = tiles_render;
}

void pascal tiles_activate_and_render_all_for_next_N_frames(uint8_t n)
{
	render_all_time = n;
	bg_render_not_bombing = tiles_render_all_timed;
}

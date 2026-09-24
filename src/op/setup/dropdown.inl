void pascal near dropdown(screen_x_t left, screen_y_t top_)
{
	mswin_tile_amount_t i;
	screen_x_t tile_left = left;
	screen_y_t top = top_;

	super_put(tile_left, top, MSWIN_LEFT_TOP);
	tile_left += MSWIN_W;
	for(i = 1; i < (window.w - 1); (i++, tile_left += MSWIN_W)) {
		super_put(tile_left, top, MSWIN_MIDDLE_TOP);
	}
	super_put(tile_left, top, MSWIN_RIGHT_TOP);

	top += MSWIN_H;
	i = 1;
	while(i < ((window.h * DROP_FRAMES_PER_TILE) - DROP_FRAMES_PER_TILE - 1)) {
		window_dropdown_put(left, top);
		frame_delay(1);
		i++;
		top += DROP_SPEED;
	}
}

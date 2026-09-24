void pascal near rollup(screen_x_t left, screen_y_t top)
{
	screen_y_t bottom_tile_top = top;
	bottom_tile_top += (window.pixel_h() - MSWIN_H);

	mswin_tile_amount_t i = 1;
	while(i < ((window.h * DROP_FRAMES_PER_TILE) - DROP_FRAMES_PER_TILE)) {
		window_rollup_put(left, bottom_tile_top);
		frame_delay(1);
		i++;
		bottom_tile_top -= DROP_SPEED;
	}
}

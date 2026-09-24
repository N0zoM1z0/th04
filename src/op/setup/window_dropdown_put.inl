void pascal near window_dropdown_put(
	screen_x_t left, screen_y_t bottom_tile_top
)
{
	egc_copy_rect_1_to_0_16(
		left,
		bottom_tile_top,
		(window.w * MSWIN_W),
		MSWIN_H
	);

	super_put(left, bottom_tile_top, MSWIN_MIDDLE_LEFT);
	super_put(left, (bottom_tile_top + DROP_SPEED), MSWIN_LEFT_BOTTOM);
	left += MSWIN_W;

	for(mswin_tile_amount_t x = 1; x < (window.w - 1); (x++, left += MSWIN_W)) {
		super_put(left, bottom_tile_top, MSWIN_INSIDE);
		super_put(left, (bottom_tile_top + DROP_SPEED), MSWIN_MIDDLE_BOTTOM);
	}

	super_put(left, bottom_tile_top, MSWIN_MIDDLE_RIGHT);
	super_put(left, (bottom_tile_top + DROP_SPEED), MSWIN_RIGHT_BOTTOM);
}

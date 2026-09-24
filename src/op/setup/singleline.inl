void pascal near singleline(screen_x_t left, screen_y_t top)
{
	egc_copy_rect_1_to_0_16(
		left,
		top,
		(window.w * MSWIN_W),
		(2 * MSWIN_H)
	);

	super_put(left, top, MSWIN_LEFT_TOP);
	super_put(left, (top + MSWIN_H), MSWIN_LEFT_BOTTOM);
	left += MSWIN_W;

	for(mswin_tile_amount_t x = 1; x < (window.w - 1); (x++, left += MSWIN_W)) {
		super_put(left, top, MSWIN_MIDDLE_TOP);
		super_put(left, (top + MSWIN_H), MSWIN_MIDDLE_BOTTOM);
	}

	super_put(left, top, MSWIN_RIGHT_TOP);
	super_put(left, (top + MSWIN_H), MSWIN_RIGHT_BOTTOM);
}

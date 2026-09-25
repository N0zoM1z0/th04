void pascal near staffroll_bgimage_expand_put(
	screen_x_t left, screen_y_t top, pixel_t w, pixel_t h, int distance
)
{
	register int half = distance;
	half /= 2;
	bgimage_put_rect_16(
		(left - half), (top - half), (w + (half * 2)), (h + (half * 2))
	);
}

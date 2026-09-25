void pascal near polygon_build(
	screen_point_t near* points,
	screen_x_t center_x,
	space_changing_pixel_t center_y,
	pixel_t radius,
	int point_count,
	unsigned char plus_angle
)
{
	int i;

	center_y.sp.v >>= SUBPIXEL_BITS;

	for(i = 0; i < point_count; i++) {
		unsigned char point_angle = (((i << 8) / point_count) + plus_angle);
		points[i].x = polar(center_x, radius, CosTable8[point_angle]);
		points[i].y = polar(center_y.pixel, radius, SinTable8[point_angle]);
	}
	points[i].x = points[0].x;
	points[i].y = points[0].y;
}

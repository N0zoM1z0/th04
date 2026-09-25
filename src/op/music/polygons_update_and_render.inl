void near polygons_update_and_render(void)
{
	int i;
	if(!polygons_initialized) {
		for(i = 0; i < POLYGONS_RENDERED; i++) {
			polygon_init(i, (irand() % to_sp(RES_Y)), (4 - (irand() & 7)));
		}

		// ZUN quirk: This is never reset.
		polygons_initialized = true;
	}
	for(i = 0; i < POLYGONS_RENDERED; i++) {
		polygon_build(
			points,
			center[i].x,
			reinterpret_cast<space_changing_pixel_t &>(center[i].y),
			(((i & 3) * 16) + 64),
			polygon_vertex_count(i),
			angle[i]
		);
		center[i].x += velocity[i].x;
		center[i].y.v += velocity[i].y.v;
		angle[i] += angle_speed[i];
		if((center[i].x <= 0) || (center[i].x >= (RES_X - 1))) {
			velocity[i].x *= -1;
		}

		// Enough to cover the maximum possible radius of 96.
		if(center[i].y >= to_sp(RES_Y + 100.0f)) {
			polygon_init(i, to_sp(-100.0f), (8 - (irand() & 15)));
		}

		grcg_polygon_c(points, polygon_vertex_count(i));
	}
}

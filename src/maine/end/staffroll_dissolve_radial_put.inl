void pascal near staffroll_dissolve_radial_put(
	screen_x_t base_left, screen_y_t base_top, int distance
)
{
	if(!distance) {
		cdg_put_8(base_left, base_top, cdg_slot);
		return;
	}
	grcg_setcolor(GC_RMW, V_WHITE);
	distance /= 4;
	int x = polar(base_left, distance, CosTable8[radial_angle]);
	int y = polar(base_top, distance, SinTable8[radial_angle]);
	cdg_put_plane(x, y, (cdg_slot + 1), 0);
	radial_angle += 0x40;
	x = polar(base_left, distance, CosTable8[radial_angle]);
	y = polar(base_top, distance, SinTable8[radial_angle]);
	cdg_put_plane(x, y, (cdg_slot + 1), 1);
	radial_angle += 0x40;
	x = polar(base_left, distance, CosTable8[radial_angle]);
	y = polar(base_top, distance, SinTable8[radial_angle]);
	cdg_put_plane(x, y, (cdg_slot + 1), 2);
	radial_angle += 0x40;
	x = polar(base_left, distance, CosTable8[radial_angle]);
	y = polar(base_top, distance, SinTable8[radial_angle]);
	cdg_put_plane(x, y, (cdg_slot + 1), 3);
	radial_angle += 0x40;
	_DX = 0x7C; _AL = 0; outportb(_DX, _AL);
}

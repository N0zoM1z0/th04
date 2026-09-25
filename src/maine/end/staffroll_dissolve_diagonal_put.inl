void pascal near staffroll_dissolve_diagonal_put(
	screen_x_t base_left, screen_y_t base_top, int distance
)
{
	if(!distance) { cdg_put_8(base_left, base_top, cdg_slot); return; }
	grcg_setcolor(GC_RMW, V_WHITE);
	distance /= 2;
	int x = polar(base_left, (distance / 2), CosTable8[96]);
	int y = polar(base_top, (distance / 2), CosTable8[32]);
	cdg_put_plane(x, y, (cdg_slot + 1), 0);
	x = polar(base_left, distance, CosTable8[64]);
	y = polar(base_top, distance, CosTable8[0]);
	cdg_put_plane(x, y, (cdg_slot + 1), 1);
	x = polar(base_left, (distance / 2), CosTable8[224]);
	y = polar(base_top, (distance / 2), CosTable8[160]);
	cdg_put_plane(x, y, (cdg_slot + 1), 2);
	x = polar(base_left, distance, CosTable8[192]);
	y = polar(base_top, distance, CosTable8[128]);
	cdg_put_plane(x, y, (cdg_slot + 1), 3);
	_DX = 0x7C; _AL = 0; outportb(_DX, _AL);
}

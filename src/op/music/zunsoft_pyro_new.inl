extern "C" void pascal near zunsoft_pyro_new(
	int origin_y, int origin_x, int n, char patnum_base
)
{
	register pyro_t near *pyro;
	register int origin_y_scaled = origin_y;
	int i;
	int pyros_created = 0;
	origin_x *= SUBPIXEL_FACTOR;
	origin_y_scaled *= SUBPIXEL_FACTOR;
	pyro = pyros;
	for(i = 0; i < 256; i++, pyro++) {
		if(!pyro->alive) {
			pyro->alive = true;
			pyro->age = 0;
			pyro->origin.x.v = origin_y_scaled;
			pyro->origin.y.v = origin_x;
			pyro->distance.v = 0;
			pyro->distance_prev.v = 0;
			pyro->speed.v = ((irand() % 224) + 64);
			pyro->angle = irand();
			pyro->patnum_base = patnum_base;
			pyros_created++;
			if(pyros_created >= n) {
				break;
			}
		}
	}
}

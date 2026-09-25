extern "C" void pascal near zunsoft_palette_update_and_show(int tone)
{
	register int color = 0;
	register int component;
	for(; color < 15; color++) {
		component = 0;
		for(; component < 3; component++) {
			Palettes[color].v[component] = (
				(zunsoft_palette[color].v[component] * tone) / 100
			);
		}
	}
	palette_show();
}

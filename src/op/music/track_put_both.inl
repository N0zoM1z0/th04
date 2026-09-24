void pascal near track_put_both(unsigned char i, unsigned char col)
{
	unsigned char other_page = (1 - music_page_accessed);
	graph_accesspage(other_page);
	graph_putsa_fx(
		TRACKLIST_LEFT,
		(8 + (i * GLYPH_H)),
		col,
		MUSIC_CHOICES[i]
	);

	graph_accesspage(music_page_accessed);
	graph_putsa_fx(
		TRACKLIST_LEFT,
		(8 + (i * GLYPH_H)),
		col,
		MUSIC_CHOICES[i]
	);
}

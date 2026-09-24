void pascal near tracklist_put_both(unsigned char sel)
{
	int i;
	for(i = 0; i < 24; i++) {
		track_put_both(i, ((i == sel) ? 3 : 5));
	}
}

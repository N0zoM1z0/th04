void pascal near cmt_load(int track)
{
	file_ropen("_MUSIC.TXT");
	file_seek((track * int(sizeof(cmt))), SEEK_SET);
	file_read(cmt, sizeof(cmt));
	file_close();
	for(int i = 0; i < CMT_LINES; i++) {
		cmt[i].c[CMT_LINE_LENGTH] = 0;
	}
}

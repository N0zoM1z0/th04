void near hiscore_scoredat_save(void)
{
	extern const char SCOREDAT_FN_2[];
	scoredat_encode();

	file_append(SCOREDAT_FN_2);

	file_seek((rank * sizeof(scoredat_section_t)), SEEK_SET);
	if(playchar != 0) {
		file_seek((5 * sizeof(scoredat_section_t)), SEEK_CUR);
	}
	file_write(&hi, sizeof(scoredat_section_t));

	for(int i = 0; i < 10; i++) {
		file_seek((i * sizeof(scoredat_section_t)), SEEK_SET);
		file_read(&hi, sizeof(scoredat_section_t));
		scoredat_decode();
		scoredat_encode();
		file_seek((i * sizeof(scoredat_section_t)), SEEK_SET);
		file_write(&hi, sizeof(scoredat_section_t));
	}
	file_close();
}

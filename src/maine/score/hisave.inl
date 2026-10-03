void near hiscore_scoredat_save(void)
{
	extern const char SCOREDAT_FN_2[];

	// loaded_score_section is decoded while the menu edits it. Encode it once,
	// then overwrite the selected rank inside the character's five-section
	// block. The filename remains a distinct external symbol for OMF layout.
	scoredat_encode();

	file_append(SCOREDAT_FN_2);

	file_seek(
		(registration_rank * sizeof(scoredat_section_t)), SEEK_SET
	);
	if(registration_playchar != 0) {
		file_seek(
			(SCOREDAT_RANKS_PER_PLAYCHAR * sizeof(scoredat_section_t)),
			SEEK_CUR
		);
	}
	file_write(&loaded_score_section, sizeof(scoredat_section_t));

	// Re-key every section, including the one just written. Decode verifies and
	// restores its payload; encode recomputes the sum and chooses fresh key
	// bytes through irand(). This intentionally rewrites all ten sections on
	// every registration save while preserving their decoded contents.
	for(int section_index = 0; section_index < SCOREDAT_SECTION_COUNT; section_index++) {
		file_seek(
			(section_index * sizeof(scoredat_section_t)), SEEK_SET
		);
		file_read(&loaded_score_section, sizeof(scoredat_section_t));
		scoredat_decode();
		scoredat_encode();
		file_seek(
			(section_index * sizeof(scoredat_section_t)), SEEK_SET
		);
		file_write(&loaded_score_section, sizeof(scoredat_section_t));
	}
	file_close();
}

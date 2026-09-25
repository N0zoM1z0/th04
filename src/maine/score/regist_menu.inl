void near regist_menu(void)
{
	register int name_pos = 0;
	register int col;
	int row;
	input_t input_locked;
	int initial_row;
	int initial_col;
	unsigned char input_delay = 0;
	unsigned char c;

	PaletteTone = 0;
	palette_show();
	graph_accesspage(1);
	pi_load(0, aHi01_pi);
	pi_palette_apply(0);
	pi_put_8(0, 0, 0);
	pi_free(0);
	graph_copy_page(0);
	super_entry_bfnt(aScnum2_bft);

	rank = ((resident->stage == STAGE_EXTRA) ? RANK_EXTRA : resident->rank);
	playchar = (resident->playchar_ascii == ('0' + PLAYCHAR_MARISA));
	hiscore_scoredat_load_for(playchar_other(playchar));
	places_put(1 - static_cast<unsigned char>(playchar));
	hiscore_scoredat_load_for(playchar);

	if(resident->turbo_mode || (rank == RANK_EXTRA)) {
		score_insert();
		places_put(static_cast<unsigned char>(playchar));
	} else {
		entered_place = -1;
		places_put(static_cast<unsigned char>(playchar));
		graph_putsa_fx(124, 196, 9, reinterpret_cast<shiftjis_t *>(aGxgnbGvbGhvVGv));
		graph_putsa_fx(120, 192, 2, reinterpret_cast<shiftjis_t *>(aGxgnbGvbGhvV_1));
	}

	if(
		(resident->end_sequence == ES_GOOD) ||
		(resident->end_sequence == ES_EXTRA) ||
		(rank == RANK_EASY)
	) {
		c = hi.score.cleared;
		if(c >= (SCOREDAT_CLEARED_BOTH + 1)) {
			c = ((resident->shottype == SHOTTYPE_A) ? SCOREDAT_CLEARED_A : SCOREDAT_CLEARED_B);
		} else {
			c |= ((resident->shottype == SHOTTYPE_A) ? SCOREDAT_CLEARED_A : SCOREDAT_CLEARED_B);
		}
		hi.score.cleared = c;
	}

	snd_kaja_func(KAJA_SONG_STOP, 0);
	snd_load(aName, SND_LOAD_SONG);
	snd_kaja_func(KAJA_SONG_PLAY, 0);
	palette_black_in(2);

	if(entered_place == 0xFF) {
		goto no_entry;
	}

	for(initial_row = 0; initial_row < ALPHABET_ROWS; initial_row++) {
		for(initial_col = 0; initial_col < ALPHABET_COLS; initial_col++) {
			gaiji_putca(
				((initial_col * 2) + 23), (initial_row + 18),
				gALPHABET[(initial_row * ALPHABET_COLS) + initial_col], TX_WHITE
			);
		}
	}
	gaiji_putca(23, 18, gALPHABET[0], (TX_GREEN | TX_REVERSE));

	col = 0;
	row = 0;
	input_reset_sense();
	input_locked = 1;

	while(1) {
		input_sense();
		if(!input_locked) {
			if(static_cast<unsigned char>(key_det) & 0x0F) {
				alphabet_cursor_put(col, row, TX_WHITE);
				if(key_det & INPUT_UP) {
					row--;
				}
				if(key_det & INPUT_DOWN) {
					row++;
				}
				if(key_det & INPUT_LEFT) {
					col--;
				}
				if(key_det & INPUT_RIGHT) {
					col++;
				}
				if(row < 0) {
					row = (ALPHABET_ROWS - 1);
				} else if(row > (ALPHABET_ROWS - 1)) {
					row = 0;
				}
				if(col < 0) {
					col = (ALPHABET_COLS - 1);
				} else if(col > (ALPHABET_COLS - 1)) {
					col = 0;
				}
				alphabet_cursor_put(col, row, (TX_GREEN | TX_REVERSE));
			}

			if((key_det & INPUT_SHOT) || (key_det & INPUT_OK)) {
				c = gALPHABET[(row * ALPHABET_COLS) + col];
				switch(c) {
				case gs_SPACE:
					c = g_EMPTY;
					goto regular;
				case gs_ARROW_LEFT:
					hi.score.g_name[entered_place][name_pos] = g_EMPTY;
					if(name_pos > 0) {
						name_pos--;
					}
					goto name_updated;
				case gs_ARROW_RIGHT:
					if(name_pos < (SCOREDAT_NAME_LEN - 1)) {
						name_pos++;
					}
					goto name_updated;
				case (gs_SPACE + 8):
					goto enter;
				default:
regular:
					hi.score.g_name[entered_place][name_pos] = c;
					if(name_pos == (SCOREDAT_NAME_LEN - 1)) {
						alphabet_cursor_put(col, row, TX_WHITE);
						col = ALPHABET_ENTER_COL;
						row = ALPHABET_ENTER_ROW;
						alphabet_cursor_put(col, row, (TX_GREEN | TX_REVERSE));
					}
					if(name_pos < (SCOREDAT_NAME_LEN - 1)) {
						name_pos++;
					}
				}
name_updated:
				name_cursor_put(entered_place, playchar, name_pos);
			}

			if(key_det & INPUT_BOMB) {
				hi.score.g_name[entered_place][name_pos] = g_EMPTY;
				if(name_pos > 0) {
					name_pos--;
				}
				name_cursor_put(entered_place, playchar, name_pos);
			}
			if(key_det & INPUT_CANCEL) {
				goto enter;
			}
			input_locked = key_det;
		} else {
			if(key_det == input_locked) {
				input_delay++;
				if((input_delay > 30) && ((input_delay & 1) == 0)) {
					input_locked = 0;
				}
			} else {
				if(key_det != INPUT_NONE) {
					optimization_barrier();
				} else {
					input_locked = 0;
				}
				input_delay = 0;
			}
		}
		input_reset_sense();
		frame_delay(1);
	}

enter:
	hiscore_scoredat_save();
	goto done;
no_entry:
	hiscore_scoredat_save();
	input_wait_for_change(0);
done:
	super_free();
	text_clear();
	palette_black_out(1);
}

void near regist_menu(void)
{
	register int name_cursor = 0;
	register int alphabet_col;
	int alphabet_row;
	input_t input_lock;
	int draw_row;
	int draw_col;
	unsigned char repeat_frames = 0;
	unsigned char selected_glyph;

	// Build the static registration screen on page 1, copy it to page 0, and
	// leave both pages synchronized before any cursor or name text is drawn.
	PaletteTone = 0;
	palette_show();
	graph_accesspage(1);
	pi_load(0, aHi01_pi);
	pi_palette_apply(0);
	pi_put_8(0, 0, 0);
	pi_free(0);
	graph_copy_page(0);
	super_entry_bfnt(aScnum2_bft);

	// The score file stores five rank sections for each character. A single
	// decoded buffer, loaded_score_section, is reused: render the other
	// character immediately, then load the current character and keep that
	// section resident for insertion, clear flags, name editing, and saving.
	registration_rank = (
		(resident->stage == STAGE_EXTRA) ? RANK_EXTRA : resident->rank
	);
	registration_playchar = (
		resident->playchar_ascii == ('0' + PLAYCHAR_MARISA)
	);
	hiscore_scoredat_load_for(playchar_other(registration_playchar));
	places_put(1 - static_cast<unsigned char>(registration_playchar));
	hiscore_scoredat_load_for(registration_playchar);

	// Only Turbo-mode scores and Extra scores enter the ranking table. The
	// other path still renders the current table, records the clear flag below,
	// and saves the section, but marks that no name can be entered.
	if(resident->turbo_mode || (registration_rank == RANK_EXTRA)) {
		score_insert();
		places_put(static_cast<unsigned char>(registration_playchar));
	} else {
		registration_place = SCOREDAT_NO_ENTRY;
		places_put(static_cast<unsigned char>(registration_playchar));
		graph_putsa_fx(124, 196, 9, reinterpret_cast<shiftjis_t *>(aGxgnbGvbGhvVGv));
		graph_putsa_fx(120, 192, 2, reinterpret_cast<shiftjis_t *>(aGxgnbGvbGhvV_1));
	}

	// Clear completion belongs to this character/rank section even if the score
	// missed the table. Values above the two-bit mask are normalized to the
	// current shot type; otherwise the current shot-type bit is accumulated.
	if(
		(resident->end_sequence == ES_GOOD) ||
		(resident->end_sequence == ES_EXTRA) ||
		(registration_rank == RANK_EASY)
	) {
		selected_glyph = loaded_score_section.score.cleared;
		if(selected_glyph >= (SCOREDAT_CLEARED_BOTH + 1)) {
			selected_glyph = (
				(resident->shottype == SHOTTYPE_A) ?
				SCOREDAT_CLEARED_A : SCOREDAT_CLEARED_B
			);
		} else {
			selected_glyph |= (
				(resident->shottype == SHOTTYPE_A) ?
				SCOREDAT_CLEARED_A : SCOREDAT_CLEARED_B
			);
		}
		loaded_score_section.score.cleared = selected_glyph;
	}

	// Switch from the Ending song to the name-entry song before fading in the
	// completed screen. This ordering is visible to the resident sound driver.
	snd_kaja_func(KAJA_SONG_STOP, 0);
	snd_load(aName, SND_LOAD_SONG);
	snd_kaja_func(KAJA_SONG_PLAY, 0);
	palette_black_in(2);

	if(registration_place == SCOREDAT_NO_ENTRY) {
		goto save_without_name;
	}

	// Draw the 3x17 gaiji keyboard, then replace the first cell with its
	// highlighted form. The final cell is the explicit Enter command.
	for(draw_row = 0; draw_row < ALPHABET_ROWS; draw_row++) {
		for(draw_col = 0; draw_col < ALPHABET_COLS; draw_col++) {
			gaiji_putca(
				((draw_col * 2) + 23), (draw_row + 18),
				name_entry_alphabet[(draw_row * ALPHABET_COLS) + draw_col],
				TX_WHITE
			);
		}
	}
	gaiji_putca(
		23, 18, name_entry_alphabet[0], (TX_GREEN | TX_REVERSE)
	);

	alphabet_col = 0;
	alphabet_row = 0;
	input_reset_sense();
	input_lock = 1;

	while(1) {
		input_sense();
		if(!input_lock) {
			if(static_cast<unsigned char>(key_det) & 0x0F) {
				alphabet_cursor_put(alphabet_col, alphabet_row, TX_WHITE);
				if(key_det & INPUT_UP) {
					alphabet_row--;
				}
				if(key_det & INPUT_DOWN) {
					alphabet_row++;
				}
				if(key_det & INPUT_LEFT) {
					alphabet_col--;
				}
				if(key_det & INPUT_RIGHT) {
					alphabet_col++;
				}
				if(alphabet_row < 0) {
					alphabet_row = (ALPHABET_ROWS - 1);
				} else if(alphabet_row > (ALPHABET_ROWS - 1)) {
					alphabet_row = 0;
				}
				if(alphabet_col < 0) {
					alphabet_col = (ALPHABET_COLS - 1);
				} else if(alphabet_col > (ALPHABET_COLS - 1)) {
					alphabet_col = 0;
				}
				alphabet_cursor_put(
					alphabet_col, alphabet_row, (TX_GREEN | TX_REVERSE)
				);
			}

			if((key_det & INPUT_SHOT) || (key_det & INPUT_OK)) {
				selected_glyph = name_entry_alphabet[
					(alphabet_row * ALPHABET_COLS) + alphabet_col
				];
				switch(selected_glyph) {
				case gs_SPACE:
					selected_glyph = g_EMPTY;
					goto store_selected_glyph;
				case gs_ARROW_LEFT:
					loaded_score_section.score.g_name
						[registration_place][name_cursor] = g_EMPTY;
					if(name_cursor > 0) {
						name_cursor--;
					}
					goto redraw_name_cursor;
				case gs_ARROW_RIGHT:
					if(name_cursor < (SCOREDAT_NAME_LEN - 1)) {
						name_cursor++;
					}
					goto redraw_name_cursor;
				case (gs_SPACE + 8):
					goto save_and_exit;
				default:
store_selected_glyph:
					loaded_score_section.score.g_name
						[registration_place][name_cursor] = selected_glyph;
					if(name_cursor == (SCOREDAT_NAME_LEN - 1)) {
						alphabet_cursor_put(
							alphabet_col, alphabet_row, TX_WHITE
						);
						alphabet_col = ALPHABET_ENTER_COL;
						alphabet_row = ALPHABET_ENTER_ROW;
						alphabet_cursor_put(
							alphabet_col, alphabet_row,
							(TX_GREEN | TX_REVERSE)
						);
					}
					if(name_cursor < (SCOREDAT_NAME_LEN - 1)) {
						name_cursor++;
					}
				}
redraw_name_cursor:
				name_cursor_put(
					registration_place, registration_playchar, name_cursor
				);
			}

			if(key_det & INPUT_BOMB) {
				loaded_score_section.score.g_name
					[registration_place][name_cursor] = g_EMPTY;
				if(name_cursor > 0) {
					name_cursor--;
				}
				name_cursor_put(
					registration_place, registration_playchar, name_cursor
				);
			}
			// Cancel confirms the current partial name; it does not discard the
			// inserted score or restore the previous table entry.
			if(key_det & INPUT_CANCEL) {
				goto save_and_exit;
			}
			input_lock = key_det;
		} else {
			if(key_det == input_lock) {
				repeat_frames++;
				if(
					(repeat_frames > NAME_REPEAT_DELAY_FRAMES) &&
					((repeat_frames & 1) == 0)
				) {
					// Releasing the lock every second held frame produces the
					// original post-delay cursor/key repeat cadence.
					input_lock = 0;
				}
			} else {
				// Semantically preserve the lock for a new nonzero input, or clear it
				// once all input is released. TC4.02 lowers this ordinary conditional
				// expression to the target direct-CMP / JZ / JMP topology.
				(key_det != INPUT_NONE) ? input_lock : (input_lock = INPUT_NONE);
				repeat_frames = 0;
			}
		}
		input_reset_sense();
		frame_delay(1);
	}

save_and_exit:
	hiscore_scoredat_save();
	goto release_resources;
save_without_name:
	hiscore_scoredat_save();
	// With no editable row, keep the completed table visible until the user
	// changes input, matching the original non-entry acknowledgement path.
	input_wait_for_change(0);
release_resources:
	super_free();
	text_clear();
	palette_black_out(1);
}

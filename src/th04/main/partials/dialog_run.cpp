void near dialog_run(void)
{
	unsigned char c;

	// ZUN bloat: An obvious remnant from the cutscene code introduced in TH03;
	// unused here.
	uint8_t speedup_cycle;

	extern shiftjis_t near dialog_kanji_buf[];
	shiftjis_t* kanji_str = dialog_kanji_buf;

	while(1) {
		// Same iteration code as in TH03's cutscene system.
		c = *(dialog_p++);
		if(str_sep_control_or_space(c)) {
			continue;
		}

		// Opcode?
		if(c == '\\') {
			c = *(dialog_p++);
			if(dialog_op(c) == STOP) {
				break;
			}
			continue;
		} else if((c == '0') || (c == '1')) {
			// Start a new dialog box by clearing it and rewinding the cursor
			if(c == '0') {
				dialog_cursor.x = to_dialog_x(TEXT_PLAYCHAR_LEFT);
				dialog_cursor.y = to_dialog_y(TEXT_PLAYCHAR_TOP);
				dialog_side = SIDE_PLAYCHAR;
			} else {
				dialog_cursor.x = to_dialog_x(TEXT_BOSS_LEFT);
				dialog_cursor.y = to_dialog_y(TEXT_BOSS_TOP);
				dialog_side = SIDE_BOSS;
			}

			dialog_box_wipe(dialog_cursor.x, dialog_cursor.y);
			speedup_cycle = 0;

			// Box loop
			while(1) {
				// ZUN bug: This would have only been necessary before, or,
				// better yet, inside dialog_delay(). It should have also been
				// the equivalent of TH05's input_reset_sense_held() instead,
				// which would have addressed the hardware quirk documented in
				// the `Research/HOLDKEY` example. Y'know, just to ensure that
				// held keys are always recognized as such, and don't cause a
				// sporadic 2-frame delay before the text is displayed
				// completely after all.
				input_reset_sense();

				// Again, same iteration code as in TH03's cutscene system.
				c = *(dialog_p++);
				if(str_sep_control_or_space(c)) {
					continue;
				}

				// Opcode?
				if(c == '\\') {
					c = *(dialog_p++);
					if(dialog_op(c) == STOP) {
						break;
					}
					continue;
				}

				// Regular kanji
				kanji_str[0] = c;
				c = *dialog_p;
				kanji_str[1] = c;
				dialog_p++;
				dialog_text_put(kanji_str);
				dialog_delay(speedup_cycle);
			}
		}
	}
	overlay_wipe();
}

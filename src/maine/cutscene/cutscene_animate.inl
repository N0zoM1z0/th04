void near cutscene_animate(void)
{
	extern ShiftJISKanji near CUTSCENE_KANJI[];

#if (GAME == 5)
	int gaiji;
#endif
	unsigned char c;
	uint8_t speedup_cycle;

	ShiftJISKanji& kanji = *CUTSCENE_KANJI;

	cursor.x = BOX_LEFT;
	cursor.y = BOX_TOP;
	text_interval = TEXT_INTERVAL_DEFAULT;
	text_col = V_WHITE;
	text_fx = FX_WEIGHT_BOLD;

#if (GAME == 3)
	speedup_cycle = 0;
#endif

	// Necessary because scripts can (and do) show multiple text boxes on the
	// initially black background.
	// ZUN landmine: TH05 assumes that they don't, which is true for all
	// scripts in the original game.
#if (GAME != 5)
	box_bg_allocate_and_snap();
#endif

	fast_forward = false;

	while(1) {
		cutscene_input_sense();
		if(key_det & INPUT_CANCEL) {
			fast_forward = true;
		} else {
			fast_forward = false;
		}

#if (GAME == 5) // ZUN bloat: Should be part of the colmap loop.
		int i = 0;
#endif

		// Same iteration code as in TH04's dialog system.
		c = *(script_p++);
		if(str_sep_control_or_space(c)) {
			continue;
		}

		// Opcode?
		if(c == '\\') {
			c = *(script_p++);
			if(script_op(c) == STOP) {
				break;
			}
			continue;
		}

#if (GAME == 5)
		if(c == '@') {
			c = tolower(*script_p);
			script_p++;
			switch(c) {
			case 't':
				gaiji = gs_SWEAT;
				break;

			case 'h':
				gaiji = gs_HEART_2;
				break;

			case '?':
				gaiji = gs_QUESTION;
				break;

			case '!':
				c = *(script_p++);
				switch(c) {
				case '!':
					gaiji = gs_DOUBLE_EXCLAMATION;
					break;

				case '?':
					gaiji = gs_EXCLAMATION_QUESTION;
					break;

				default:
					script_p--;
					gaiji = gs_EXCLAMATION;
					break;
				}
				break;

			default:
				script_p--;
				script_param_read_number_first(gaiji, gs_NOTES);
				break;
			}
			graph_showpage(0);
			graph_accesspage(1);

			// Still ignoring [text_fx].
			graph_gaiji_putc(cursor.x, cursor.y, gaiji, text_col);

			cursor_advance_and_animate();
			i = 1; // ZUN bloat
			continue;
		}
#endif

		// Regular kanji
		kanji.byte[0] = c;
		c = *script_p;
		kanji.byte[1] = c;
		script_p++;

#if (GAME == 5)
		if(cursor.x == BOX_LEFT) {
			for(i = 0; i < colmap_count; i++) {
				if(colmap.keys[i][0].t == kanji.t) {
					text_col = colmap.values[i];
					break;
				}
			}
		}
#endif

#if (GAME >= 4)
		graph_showpage(0);
		graph_accesspage(1);
		graph_putsa_fx(cursor.x, cursor.y, text_col, kanji.byte);
#else
		graph_accesspage(1);
		graph_putsa_fx(cursor.x, cursor.y, (text_col | text_fx), kanji.byte);
		graph_accesspage(0);
		graph_putsa_fx(cursor.x, cursor.y, (text_col | text_fx), kanji.byte);
#endif
#if (GAME == 5)
		// ZUN bloat: All blitting operations in this module access the
		// intended page before they blit. That's why preliminary state
		// changes like this one are completely redundant, thankfully.
		graph_accesspage(0);
#endif
		cursor_advance_and_animate();
#if (GAME == 5)
		i = 1; // ZUN bloat
#endif

		// High-level overview, point 3)
#if (GAME == 3)
		if(fast_forward) {
			continue;
		}
		if(key_det == INPUT_NONE) {
			frame_delay(text_interval);
		} else {
			int speedup_interval = (text_interval / 3);
			if((speedup_cycle & 1) || speedup_interval) {
				if(speedup_interval == 0) {
					speedup_interval++;
				}
				frame_delay(speedup_interval);
			}
			speedup_cycle++;
		}
#endif
	}
#if (GAME == 5)
	bgimage_free();
	pi_free(CUTSCENE_PIC_SLOT);
#else
	box_bg_put();
	box_bg_free();
#endif
}

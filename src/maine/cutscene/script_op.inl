script_ret_t pascal near script_op(unsigned char c)
{
	// ZUN bloat: Needed for code generation reasons. The structure of the
	// conditional branches below ensures that the `return`s have no actual
	// effect, so this block can just be deleted.
#if (GAME == 5)
	#define palette_black_in(x)  palette_black_in(x);  return CONTINUE;
	#define palette_black_out(x) palette_black_out(x); return CONTINUE;
	#define palette_white_in(x)  palette_white_in(x);  return CONTINUE;
	#define palette_white_out(x) palette_white_out(x); return CONTINUE;
#endif

	int i;
	int p1;
	int p2;

	// ZUN bloat: PF_FN_LEN on its own is enough, it already includes the \0
	// terminator.
	char fn[PF_FN_LEN + 3];

	c = tolower(c);
	switch(c) {
	case 'n':
		cursor.y += GLYPH_H;
		cursor.x = BOX_LEFT;
		if(cursor.y < BOX_BOTTOM) {
			break;
		}
		// ZUN quirk: Since [cursor.y] is >= BOX_BOTTOM here, the TH05 Return
		// key animation will be displayed at the right edge of the "5th" line,
		// below BOX_BOTTOM. (Same issue as in cursor_advance_and_animate().)

		// fallthrough to \s if this box is full

	case 's':
		c = *script_p;
#if (GAME >= 4)
		box_1_to_0_animate();
#endif
		if(c != '-') {
			script_param_read_number_first(p1, 0);
			if(!fast_forward) {
				box_wait_animate(p1);
			}
		} else {
			script_p++;
		}
		cursor.x = BOX_LEFT;
		cursor.y = BOX_TOP;

#if (GAME == 5)
		graph_accesspage(1);
		bgimage_put_rect_16(BOX_LEFT, BOX_TOP, BOX_W, BOX_H);

		// ZUN bloat: All blitting operations in this module access the
		// intended page before they blit. That's why preliminary state
		// changes like this one are completely redundant, thankfully.
		graph_accesspage(0);
#else
		// High-level overview, point 2)
		graph_accesspage(1);	box_bg_put();
		graph_accesspage(0);	box_bg_put();
#endif
		break;

	case 'c':
#if (GAME == 5)
		// ZUN bloat: Doesn't matter for either '=' or digits.
		c = tolower(*script_p);

		if(c == '=') {
			goto colmap_add;
		}
#endif
		script_param_read_number_first(p1, V_WHITE);
		text_col = p1;
		break;

	case 'b':
		script_param_read_number_first(p1, WEIGHT_BOLD);
#if (GAME >= 4)
		graph_putsa_fx_func = static_cast<graph_putsa_fx_func_t>(p1);
#else
		switch(p1) {
		case WEIGHT_NORMAL:	text_fx = FX_WEIGHT_NORMAL;	break;
		case WEIGHT_HEAVY: 	text_fx = FX_WEIGHT_HEAVY; 	break;
		case WEIGHT_BOLD:  	text_fx = FX_WEIGHT_BOLD;  	break;
		case WEIGHT_BLACK: 	text_fx = FX_WEIGHT_BLACK; 	break;
		}
#endif
		break;

	case 'w':
		c = tolower(*script_p);
		if((c == 'o') || (c == 'i')) {
			script_op_fade(c, palette_white_in, palette_white_out, p1);
		} else {
#if (GAME >= 4)
			box_1_to_0_animate();
#endif
			script_param_number_default = 64;
			if(c != 'm') {
				if(c == 'k') {
					script_p++;
				}
				script_param_read_number_first(p1);
				if(!fast_forward) {
#if (GAME >= 4)
					frame_delay(p1);
#else
					if(c != 'k')  {
						frame_delay(p1);
					} else {
						input_wait_for_ok(p1);
					}
#endif
#if (GAME == 5) // ZUN bloat
					return CONTINUE;
#endif
				}
			} else {
				script_p++;
				c = *script_p;
				if(c == 'k') {
					script_p++;
				}
				script_param_read_number_first(p1);
				script_param_read_number_second(p2);
				if(!fast_forward) {
					// ZUN landmine: Does not prevent the potential deadlock
					// issue with this function.
#if (GAME >= 4)
					snd_delay_until_measure(p1, p2);
#else
					if(c != 'k')  {
						snd_delay_until_measure(p1, p2);
					} else {
						input_wait_for_ok_or_measure(p1, p2);
					}
#endif
				}
			}
		}
		break;

	case 'v':
		if(*script_p != 'p') {
			script_param_read_number_first(p1, TEXT_INTERVAL_DEFAULT);
			text_interval = p1;
		} else {
			script_p++;
			script_param_read_number_first(p1, 0);
			graph_showpage(p1);
		}
		break;

	case 't':
		script_param_read_number_first(p1, 100);
		if(!fast_forward) {
			frame_delay(1);
		}
		palette_settone(p1);
		break;

	case 'f':
		c = *script_p;
		if(c != 'm') {
			if((c == 'i') || (c == 'o')) {
				script_op_fade(c, palette_black_in, palette_black_out, p1);
			}
		} else {
			script_p++;
			script_param_read_number_first(p1, 1);

			// ZUN landmine: Should restrict [p1] to 8 bits – otherwise, the
			// parameter would overflow into the function and not make this a
			// fade. (The regular snd_kaja_func() behaves this way.)
			snd_kaja_interrupt((KAJA_SONG_FADE << 8) + p1);

#if (GAME <= 4) // ZUN bloat: `break` or `return`, pick one!
			return CONTINUE;
#endif
		}
		break;

	case 'g':
		if((GAME == 5) || (*script_p != 'a')) {
			script_op_shake(fast_forward, p2, p1);
		} else {
			script_p++;
			script_param_read_number_first(p1, 0);

			graph_accesspage(1);
#if (GAME == 3)
			// Looks like a ZUN bug, but actually works around the master.lib
			// bug mentioned in the comment of this function, which ZUN only
			// fixed for TH04 and TH05. In the original binary, the ASCII→digit
			// conversion inside str_consume_up_to_3_digits() is done by ADDing
			// a negative number, which causes the x86 carry flag to always be
			// set when we get here and haven't fallen back onto the default
			// value. Therefore, the bug will always add 1 onto the gaiji ID,
			// which can be worked around by subtracting 1 before passing it as
			// a parameter. Once graph_gaiji_putc() returns, the carry flag
			// happens to be cleared, which is why the subtraction is not
			// necessary for the call below to display the intended gaiji.
			graph_gaiji_putc(cursor.x, cursor.y, (p1 - 1), text_col);

			graph_accesspage(0);
#endif
			// [text_fx] is also ignored here...
			graph_gaiji_putc(cursor.x, cursor.y, p1, text_col);
			// ZUN quirk: No [text_interval]-based delay in TH03.

			cursor_advance_and_animate();
		}
		return CONTINUE;

	case 'k':
		// ZUN landmine: Should have also been done in TH04. Without this call,
		// this command will wait on an invisible text box, and needs to be
		// preceded by a \vp1 command to actually work as a mid-box pause.
#if (GAME == 5)
		box_1_to_0_animate();
#endif

		script_param_read_number_first(p1, 0);
		if(!fast_forward) {
			// ZUN quirk: This parameter is ignored in TH03. Labeling this as a
			// quirk because the original TH03 scripts call this command with a
			// non-0 parameter in 19 of 34 cases, suggesting that ZUN made the
			// conscious decision to override these parameters with 0 later in
			// development.
			box_wait_animate((GAME >= 4) ? p1 : 0);
		}
		return CONTINUE;

	case '@':
		graph_accesspage(1);	graph_clear();
		graph_accesspage(0);	graph_clear();
#if (GAME == 5)
		bgimage_snap();
#else
		// ZUN landmine: Missing a box_bg_allocate_and_snap() or equivalent
		// call. Any future box_bg_put() call will still display the box area
		// snapped from any previously displayed background image. This bug
		// therefore effectively restricts usage of this command to either the
		// beginning of a script (before the first background image is shown)
		// or its end (after no more new text boxes are started).
#endif
		break;

	case 'p':
		c = *script_p;
		script_p++;

		// ZUN landmine: Blitting and palette changes will cause screen tearing
		// if done outside of VBLANK. It shouldn't be the script's
		// responsibility to prevent that.
		if((c == '=') || (c == '@')) {
			graph_accesspage(1);
			if(c == '=') {
				pi_palette_apply(CUTSCENE_PIC_SLOT);
			}
			pi_put_8(0, 0, CUTSCENE_PIC_SLOT);
			graph_copy_page(0);
			graph_accesspage(0);
#if (GAME == 5)
			bgimage_snap();
#else
			box_bg_allocate_and_snap();
#endif
		} else if(c == '-') {
			pi_free(CUTSCENE_PIC_SLOT);
			return CONTINUE;
		} else if(c == 'p') {
			pi_palette_apply(CUTSCENE_PIC_SLOT);
			return CONTINUE;
		} else if(c != ',') {
			script_p--;
		} else {
			script_param_read_fn(fn, p1, c);
#if (GAME >= 4)
			pi_free(CUTSCENE_PIC_SLOT);
#endif
			pi_load(CUTSCENE_PIC_SLOT, fn);
		}
		break;

	case '=':
		script_param_number_default = PI_QUARTER_COUNT;
		c = *script_p;

		// ZUN landmine: Same screen tearing issues here. TH05's frame_delay()
		// call prevents them for immediate blitting, but not for crossfading.
		if(c != '=') {
			script_param_read_number_first(p1);
#if (GAME == 5)
			frame_delay(1);
			graph_showpage(0);
			graph_accesspage(1);
#else
			// ZUN bloat: Why did ZUN temporarily switch foreground and
			// background pages for the duration of this command?! Not only is
			// it completely unnecessary, it's also downright harmful. If these
			// lines didn't exist, the entire cutscene system would have been
			// both much easier to understand *and* more performant:
			//
			// • The intent for both VRAM pages would have been crystal clear:
			//   Page 0 is always shown and contains the actively displayed
			//   picture and text, and page 1 is used for temporarily storing
			//   pixels that are later crossfaded onto page 0. Through their
			//   mere existence, these lines suggest a more complex interplay
			//   between the two pages, which doesn't actually exist.
			// • TH03 wouldn't have needed to render text and gaiji to both
			//   VRAM pages.
			// • (Technically, TH03 wouldn't have even needed [box_bg] as a
			//   result, but that was a decent investment regardless –
			//   inter-page blitting is horribly slow no matter how you do it.
			//   Also, this buffer does become necessary in TH04 – see point 2)
			//   in the high-level overview)
			// • If \vp didn't exist (it's not used by the original scripts
			//   anyway), the entire system would have only needed a single
			//   graph_showpage(0) call at the start of cutscene_animate().
			//
			// ZUN landmine: Since TH04 renders text to VRAM page 1, calling \=
			// or \== in the middle of a string of text temporarily shows any
			// text rendered since the last box_1_to_0_animate() call if any of
			// the following blit operations spends more than one frame with
			// page 1 visible. In practice, this only happens on very
			// underclocked systems far below the game's target of 66 MHz, but
			// it's a landmine nonetheless.
			graph_showpage(1);
			graph_accesspage(0);
#endif
			if(p1 < PI_QUARTER_COUNT) {
				pi_put_quarter_8(
					CUTSCENE_PIC_LEFT, CUTSCENE_PIC_TOP, CUTSCENE_PIC_SLOT, p1
				);
			} else {
				grcg_setcolor(GC_RMW, 0);
				grcg_boxfill_8(
					CUTSCENE_PIC_LEFT,
					CUTSCENE_PIC_TOP,
					(CUTSCENE_PIC_LEFT + CUTSCENE_PIC_W - 1),
					(CUTSCENE_PIC_TOP  + CUTSCENE_PIC_H - 1)
				);
				grcg_off();
			}
		} else {
			script_p++;
			script_param_read_number_first(p1);
			script_param_number_default = 1;
			script_param_read_number_second(p2);
			for(i = 0; i < PI_MASK_COUNT; i++) {
				pic_put_both_masked(CUTSCENE_PIC_LEFT, CUTSCENE_PIC_TOP, p1, i);
				if(!fast_forward) {
					frame_delay(p2);
				}
			}
#if (GAME == 5)
			graph_accesspage(1);
			pi_put_quarter_8(
				CUTSCENE_PIC_LEFT, CUTSCENE_PIC_TOP, CUTSCENE_PIC_SLOT, p1
			);
			frame_delay(1); // ZUN quirk
#else
			// ZUN bloat: See above.
			// ZUN landmine: See above.
			graph_showpage(1);
			graph_accesspage(0);

			pi_put_quarter_8(
				CUTSCENE_PIC_LEFT, CUTSCENE_PIC_TOP, CUTSCENE_PIC_SLOT, p1
			);
#endif
		}
#if (GAME <= 4)
		graph_showpage(0); // ZUN bloat: See above.
#endif
		static_assert(CUTSCENE_PIC_W == PI_QUARTER_W);
		static_assert(CUTSCENE_PIC_H == PI_QUARTER_H);
		pic_copy_to_other(CUTSCENE_PIC_LEFT, CUTSCENE_PIC_TOP);
		break;

	case 'm':
		// TH03 uses the TH02 version of snd_load(), and consequently does the
		// right thing and stops any currently playing BGM before loading the
		// new one. It wouldn't be necessary for TH04 and TH05, but hey, still
		// doing it removes a potential implementation difference.
		script_op_bgm(true, c, fn, p1);
		break;

	case 'e':
		script_param_read_number_first(p1);
		snd_se_play_force(p1);
		break;

#if (GAME == 5)
colmap_add:
	script_p++;
	colmap.keys[colmap_count][0].byte[0] = *script_p;
	script_p++;
	colmap.keys[colmap_count][0].byte[1] = *script_p;

	// ZUN landmine: Jumps over the additional comma separating the two
	// parameters, and assumes it's always present. Come on!
	// script_param_read_number_second() exists to handle exactly this
	// situation in a cleaner way.
	script_p += 2;

	script_param_read_number_first(p1, V_WHITE);

	// ZUN landmine: No bounds check
	colmap.values[colmap_count] = p1;
	colmap_count++;
	break;
#endif

	case '$':
		return STOP;
	}
	return CONTINUE;
}

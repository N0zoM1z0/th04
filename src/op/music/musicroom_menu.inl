void MUSICROOM_DISTANCE musicroom_menu(void)
{
#if (GAME == 5)
	int frame_since_last_input = 0;
	uint8_t sel_prev;
	track_id_at_top = 0;
	track_playing = 0;
	music_sel = 0;
	track_count_cur = TRACK_COUNT[game_sel];
	#define SEL_QUIT track_count_cur
#else
	enum {
		SEL_QUIT = (TRACK_COUNT + 1),
	};
#endif

#if (GAME >= 4)
	cmt_shown_initial = false;
#endif

	// ZUN bloat: The call site would have been a better place for this.
#if (GAME >= 4)
	cdg_free_all();
	text_clear();
#elif (GAME == 3)
	for(int i = 0; i < CDG_SLOT_COUNT; i++) {
		cdg_free(i);
	}
	super_free();
	text_clear();
#endif

	music_page_accessed = 1;

	palette_settone(0);
	graph_showpage(0);

	// ZUN bloat: We copy page 1 to page 0 below anyway. The hardware palette
	// is also entirely black, so no one will ever see a difference.
	graph_accesspage(0);
	graph_clear();

	graph_accesspage(1);

#if (GAME >= 4)
	pi_fullres_load_palette_apply_put_free(0, "music.pi");
#else
	pi_fullres_load_palette_apply_put_free(0, "op3.pi");
#endif

#if (GAME == 5)
	piano_setup_and_put_initial();
	nopoly_B_snap();
	bgimage_snap();
	tracklist_put(music_sel);
#else
	music_sel = track_playing;

	// ZUN bloat: We copy pages below anyway, this doesn't need to be blitted
	// to both.
	tracklist_put_both(music_sel);
#endif
	graph_copy_page(0);

#if (GAME == 4)
	bgimage_snap();
#endif
	graph_accesspage(1);
	graph_showpage(0);

#if (GAME <= 4)
	nopoly_B_snap();
#endif

#if (GAME == 5)
	pfend();
	pfstart("music.dat");
	cmt_load_unput_and_put_both_animate(music_sel);
#elif (GAME == 4)
	cmt_load_unput_and_put_both_animate(track_playing);
#else
	cmt_bg_snap();
	graph_accesspage(1);	cmt_load_unput_and_put(track_playing);
	graph_accesspage(0);	cmt_load_unput_and_put(track_playing);
#endif

	// ZUN landmine: After all the loading and blitting, we're certainly in the
	// middle of a frame, where a sudden change to the hardware palette ensures
	// tearing.
	palette_100();

	while(1) {
		// In TH05, this loop also ignores any ← or → inputs while ↑ or ↓ are
		// held, and vice versa.
		// ZUN bloat: None of this `goto` business would have been necessary if
		// the loop clearly defined its update and render steps. Especially
		// since it does want to render the polygon animation every frame.
		while(1) {
			music_input_sense();
			if(!key_det) {
				break;
			}
#if (GAME == 5)
			if(frame_since_last_input >= 24) {
				if((key_det == INPUT_UP) || (key_det == INPUT_DOWN)) {
					frame_since_last_input = 20;
					break;
				}
			}
			frame_since_last_input++;
#endif
			music_update_render_and_flip();
		}
controls:
		// ZUN bloat: We already did that for this frame if we came from above,
		// but not if we came from the `goto` below.
		music_input_sense();

#if (GAME == 5)
		if(key_det & INPUT_UP) {
			sel_prev = music_sel;
			if(music_sel > 0) {
				music_sel--;
				if(music_sel < track_id_at_top) {
					track_id_at_top = music_sel;
					tracklist_unput_and_put_both_animate(music_sel);

					// ZUN quirk: This prevents game switches via ← or → , but
					// only in the very specific case of
					// 1) the cursor being at the top of the list,
					// 2) highlighting a track other than the first one of the
					//    respective game, and
					// 3) ←/→ being pressed simultaneously with ↑.
					//    In any other case, ←/→ are processed as expected, and
					//    override this cursor movement with a game switch.
					goto skip_processing_of_left_and_right;
				} else {
					track_unput_and_put_both_animate(sel_prev, music_sel);
				}
			} else {
				music_sel = SEL_QUIT;
				track_id_at_top = (
					SEL_QUIT - (TRACKLIST_VISIBLE_COUNT - 1)
				);
				tracklist_unput_and_put_both_animate(SEL_QUIT);
			}
		}
		if(key_det & INPUT_DOWN) {
			sel_prev = music_sel;
			if(music_sel < SEL_QUIT) {
				music_sel++;
				if(music_sel >= (track_id_at_top + TRACKLIST_VISIBLE_COUNT)) {
					track_id_at_top = (
						music_sel - (TRACKLIST_VISIBLE_COUNT - 1)
					);
					tracklist_unput_and_put_both_animate(music_sel);

					// Same as the quirk above, applying to the
					// corresponding very specific case of
					// 1) the cursor being at the bottom of the list,
					// 2) highlighting anything except [SEL_QUIT], and
					// 3) ←/→ being pressed simultaneously with ↓.
					goto skip_processing_of_left_and_right;
				} else {
					track_unput_and_put_both_animate(sel_prev, music_sel);
				}
			} else {
				music_sel = 0;
				track_id_at_top = 0;
				tracklist_unput_and_put_both_animate(music_sel);
			}
		}
		if(key_det & INPUT_LEFT) {
			ring_dec(game_sel, (GAME_COUNT - 1));
			game_switch();
		} else if(key_det & INPUT_RIGHT) {
			ring_inc_ge(game_sel, GAME_COUNT);
			game_switch();
		}
#else
		if(key_det & INPUT_UP) {
			track_put_both(music_sel, COL_TRACKLIST);
			if(music_sel > 0) {
				music_sel--;
			} else {
				music_sel = SEL_QUIT;
			}

			// Skip over the empty line
			if(music_sel == TRACK_COUNT) {
				music_sel--;
			}

			track_put_both(music_sel, COL_TRACKLIST_SELECTED);
		}
		if(key_det & INPUT_DOWN) {
			track_put_both(music_sel, COL_TRACKLIST);
			if(music_sel < SEL_QUIT) {
				music_sel++;
			} else {
				music_sel = 0;
			}

			// Skip over the empty line
			if(music_sel == TRACK_COUNT) {
				music_sel++;
			}

			track_put_both(music_sel, COL_TRACKLIST_SELECTED);
		}
#endif
	skip_processing_of_left_and_right:
		if(key_det & INPUT_SHOT || key_det & INPUT_OK) {
			if(music_sel != SEL_QUIT) {
#if (GAME >= 4)
				snd_kaja_func(KAJA_SONG_FADE, 32);
#elif (GAME == 3)
				// Avoids the snd_load() landmine that is still present in this
				// game.
				snd_kaja_func(KAJA_SONG_STOP, 0);
#elif (GAME == 2)
				// ZUN landmine: Should have stopped the currently playing
				// track according to snd_load()'s header comment.
				// Especially since this game simultaneously loads both the PMD
				// and MIDI versions and is therefore inherently slower than
				// the others.
#endif
#if (GAME == 5)
				sel_prev = track_playing;
				track_playing = music_sel;
				track_unput_and_put_both_animate(sel_prev, music_sel);
				cmt_load_unput_and_put_both_animate(music_sel);
				snd_load(MUSIC_FILES[game_sel][music_sel], SND_LOAD_SONG);
				snd_kaja_func(KAJA_SONG_PLAY, 0);
#elif (GAME == 4)
				track_playing = music_sel;
				cmt_load_unput_and_put_both_animate(music_sel);
				snd_load(MUSIC_FILES[music_sel], SND_LOAD_SONG);
				snd_kaja_func(KAJA_SONG_PLAY, 0);
#else
#if (GAME == 3)
				snd_load(MUSIC_FILES[music_sel], SND_LOAD_SONG);
#else
				// Load both the MIDI and PMD versions of the selected track.
				// Makes sense given that the track continues playing when
				// leaving the Music Room – changing the music mode in the
				// Option menu will then play the same selected track.
				bool midi_active = snd_midi_active;
				snd_midi_active = snd_midi_possible;
				snd_load(MUSIC_FILES[music_sel], SND_LOAD_SONG);
				snd_midi_active = 0;
				snd_load(MUSIC_FILES[music_sel], SND_LOAD_SONG);
				snd_midi_active = midi_active;
#endif
				snd_kaja_func(KAJA_SONG_PLAY, 0);
				track_playing = music_sel;
				cmt_load_unput_and_put(music_sel);
				music_update_render_and_flip();
				cmt_load_unput_and_put(music_sel);
#endif
			} else {
				break;
			}
		}
		if(key_det & INPUT_CANCEL) {
			break;
		}
		if(!key_det) {
#if (GAME == 5)
			frame_since_last_input = 0;
#endif
			music_update_render_and_flip();
			goto controls;
		}
	};

	// Wait until the player released the key that broke out of the loop
	while(1) {
		music_input_sense();
		if(!key_det) {
			break;
		}
		music_update_render_and_flip();
	}

#if (GAME == 5)
	pfend();
	pfstart(OP_AND_END_PF_FN);
#endif
#if (GAME >= 4)
	snd_kaja_func(KAJA_SONG_FADE, 16);
	nopoly_B_free();
	graph_showpage(0);
	graph_accesspage(0);
	palette_black_out(1);
	bgimage_free();
	snd_load(BGM_MENU_MAIN_FN, SND_LOAD_SONG);
	snd_kaja_func(KAJA_SONG_PLAY, 0);
#else
	nopoly_B_free();
	cmt_bg_free();
	graph_showpage(0);

	// ZUN quirk: graph_clear() sets all of VRAM to hardware color #0, which is
	// purple in the original images, not black.
	// Since [PaletteTone] also stays at 100, this clear call is not as useless
	// as it seems. The alternative of setting all other colors to color #0
	// would even cause additional tearing at the pi_palette_apply() call
	// below, which is sandwiched between the expensive calls to pi_load() and
	// pi_put_8() and negates any palette tricks.
	graph_accesspage(0);
	graph_clear();

	graph_accesspage(1);

#if (GAME == 2)
	// ZUN bloat: The call site would have been a better place for this,
	// especially since it has another copy of the same code with the same
	// landmine.
	pi_fullres_load_palette_apply_put_free(0, MENU_MAIN_BG_FN);
	palette_entry_rgb_show(MENU_MAIN_PALETTE_FN);
	graph_copy_page(0);
#endif

	graph_accesspage(0);
#endif
}

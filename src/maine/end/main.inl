void main(void)
{
#if (GAME == 4)
	char* congratulations_pic_fn = "CONG00.pi";
#endif

	if(!cfg_load_resident_ptr()) {
		return;
	}

#if (GAME == 4)
	congratulations_pic_fn[4] = resident->playchar_ascii;
#endif

	mem_assign_paras = (336000 >> 4);
	game_init_main(OP_AND_END_PF_FN);
#if (GAME == 4)
	gaiji_backup();
	gaiji_entry_bfnt(GAIJI_FN);
#endif
	snd_determine_modes(resident->bgm_mode, resident->se_mode);
#if (GAME == 5)
	snd_load(SE_FN, SND_LOAD_SE);
	graph_show();
	random_seed = resident->rand;
	frame_delay(100);
#else
	graph_show();
#endif

	static_assert(ES_GOOD > ES_BAD);
	if(resident->end_sequence >= ES_BAD) {
		end_animate();
		staffroll_animate();
#if (GAME == 4)
		verdict_animate();

		// The rank condition causes the congratulation image to be shown for
		// the enforced Bad Ending after clearing Stage 5 on Easy Mode,
		// regardless of whether the player continued or not. You might
		// consider it a quirk to show 「EASY ALL CLEAR!!」 for a ≥2CC, but
		// 「Try to Normal Rank!!」 could very well be ZUN's roundabout way of
		// implying "because this is how you avoid the Bad Ending".
		if(
			(resident->end_sequence == ES_GOOD) || (resident->rank == RANK_EASY)
		) {
			congratulations_pic_fn[5] += resident->rank;
			congratulations_animate(congratulations_pic_fn);
		}
		snd_kaja_func(KAJA_SONG_FADE, 4);
#endif
		delay_then_regist_menu();
	} else if(resident->end_sequence == ES_EXTRA) {
#if (GAME == 5)
		end_animate();
		allcast_animate();
		verdict_animate();
		delay_then_regist_menu();
#else
		delay_then_regist_menu();
		congratulations_pic_fn[5] = ('0' + RANK_EXTRA);
		palette_settone(0);
		congratulations_animate(congratulations_pic_fn);
		verdict_animate();
#endif
	} else { // resident->end_sequence == ES_SCORE
		delay_then_regist_menu();
		verdict_animate();
	}
	snd_kaja_func(KAJA_SONG_FADE, 4);
	game_exit_and_exec(BINARY_OP);
}

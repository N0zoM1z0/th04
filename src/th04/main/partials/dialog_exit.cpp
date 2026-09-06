void near dialog_exit(void)
{
	#undef BOMB_BG_REIMU_FN
	#undef BOMB_BG_MARISA_FN
	#undef FACESET_MUGETSU_DEFEAT_FN
	#undef FACESET_GENGETSU_DEFEAT_FN
	extern const char BOMB_BG_REIMU_FN[];
	extern const char BOMB_BG_MARISA_FN[];
	extern const char FACESET_MUGETSU_DEFEAT_FN[];
	extern const char FACESET_GENGETSU_DEFEAT_FN[];

	int i;

	for(i = CDG_FACESET_PLAYCHAR; i < (CDG_FACESET_PLAYCHAR_last + 1); i++) {
		cdg_free(i);
	}
	if(stage_id == STAGE_EXTRA) {
		// MODDERS: This assumes that BSS6.CD2, BSS7.CD2, and BSS8.CD2 each
		// have at most 3 slots, rather than up to FACESET_BOSS_COUNT.
		for(i = CDG_FACESET_BOSS; i < (CDG_FACESET_BOSS + 3); i++) {
			cdg_free(i);
		}

		// What's a function parameter? :zunpet:
		extern uint8_t number_of_calls_to_this_function_during_extra;
		if((number_of_calls_to_this_function_during_extra++) == 0) {
			cdg_load_all(CDG_FACESET_BOSS, FACESET_MUGETSU_DEFEAT_FN);
		} else {
			cdg_load_all(CDG_FACESET_BOSS, FACESET_GENGETSU_DEFEAT_FN);
		}
	}

	if(Ems) {
		playchar_bomb_bg_load_from_ems();
	} else {
		if(playchar == PLAYCHAR_REIMU) {
			cdg_load_single_noalpha(CDG_BG_PLAYCHAR_BOMB, BOMB_BG_REIMU_FN, 0);
		} else {
			cdg_load_single_noalpha(CDG_BG_PLAYCHAR_BOMB, BOMB_BG_MARISA_FN, 0);
		}
	}
}

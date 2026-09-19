#ifndef TH04_MAIN_SHIFTJIS_FNS_HPP
#define TH04_MAIN_SHIFTJIS_FNS_HPP

#if (GAME == 5)
#define FACESET_REIMU_FN  "KAO0.cd2"
#define FACESET_MARISA_FN "KAO1.cd2"
#define FACESET_MIMA_FN   "KAO2.cd2"
#define FACESET_YUUKA_FN  "KAO3.cd2"

#define main_cdg_load_faceset_playchar() { \
	switch(playchar) { \
	case PLAYCHAR_REIMU: \
		cdg_load_all(CDG_FACESET_PLAYCHAR, FACESET_REIMU_FN); \
		break; \
	case PLAYCHAR_MARISA: \
		cdg_load_all(CDG_FACESET_PLAYCHAR, FACESET_MARISA_FN); \
		break; \
	case PLAYCHAR_MIMA: \
		cdg_load_all(CDG_FACESET_PLAYCHAR, FACESET_MIMA_FN); \
		break; \
	case PLAYCHAR_YUUKA: \
		cdg_load_all(CDG_FACESET_PLAYCHAR, FACESET_YUUKA_FN); \
		break; \
	} \
}
#else
#define FACESET_REIMU_FN  "KAO0.CD2"
#define FACESET_MARISA_FN "KAO1.CD2"

#define main_cdg_load_faceset_playchar() { \
	if(playchar == PLAYCHAR_REIMU) { \
		cdg_load_all(CDG_FACESET_PLAYCHAR, FACESET_REIMU_FN); \
	} else { \
		cdg_load_all(CDG_FACESET_PLAYCHAR, FACESET_MARISA_FN); \
	} \
}
#endif

#endif

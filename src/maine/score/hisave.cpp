#include "src/maine/score/scoredat.hpp"
#include "src/shared/runtime/api.hpp"

extern unsigned char rank;
#define registration_rank rank
extern unsigned char playchar;
#define registration_playchar playchar

#define loaded_score_section hi

enum {
    SCOREDAT_RANKS_PER_PLAYCHAR = 5,
    SCOREDAT_SECTION_COUNT = 10,
};


unsigned char pascal near scoredat_decode(void);
unsigned char pascal near scoredat_encode(void);

#if defined(TH04P)
#pragma codeseg SCORE_TEXT GROUP_01
#else
#pragma codeseg SCORE_TEXT score_01
#endif
#include "src/maine/score/hisave.inl"
#pragma codeseg

#include "src/maine/score/scoredat.hpp"
#include "src/maine/score/playchar.hpp"
#include "src/shared/runtime/api.hpp"

extern unsigned char rank;
#define registration_rank rank
#define loaded_score_section hi

enum {
    SCOREDAT_RANKS_PER_PLAYCHAR = 5,
};
extern const char SCOREDAT_FN_0[];
extern const char SCOREDAT_FN_1[];
unsigned char pascal near scoredat_decode(void);
void near scoredat_recreate(void);

#if defined(TH04P)
#pragma codeseg SCORE_TEXT GROUP_01
#else
#pragma codeseg SCORE_TEXT score_01
#endif
#include "src/maine/score/load_for.inl"
#pragma codeseg

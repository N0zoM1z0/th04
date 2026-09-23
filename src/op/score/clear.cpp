// OP SCORE_TEXT registration-view clear flags and glyph loading.
#include "src/op/score/scoredat.hpp"
#include "src/shared/platform/types.hpp"
#include "src/shared/config/resident.hpp"
#include "src/shared/hardware/graphics.hpp"

extern unsigned char rank;
extern unsigned char cleared_with[2][5];
extern bool extra_unlocked;

bool near hiscore_scoredat_load_both(void);

enum {
    PLAYCHAR_REIMU = 0,
    PLAYCHAR_MARISA = 1,
    RANK_EASY = 0,
    RANK_COUNT = 5,
    SCOREDAT_CLEARED_BOTH = 3,
};

#pragma codeseg SCORE_TEXT op_01
#include "src/op/score/clear_sprites_load.inl"
#pragma codeseg

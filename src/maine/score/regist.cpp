#include "src/shared/platform/types.hpp"
#include "src/maine/score/scoredat.hpp"
#include "src/maine/score/playchar.hpp"
#include "src/shared/config/resident.hpp"
#include "src/shared/platform/pc98.hpp"
#include "src/shared/hardware/graphics.hpp"
#include "src/shared/hardware/gaiji.hpp"
#include "src/shared/hardware/putsa.hpp"
#include "src/shared/hardware/input.hpp"
#include "src/shared/hardware/frame_delay.hpp"
#include "src/shared/formats/pi.hpp"
#include "src/shared/sound/api.hpp"

extern unsigned char rank;
#define registration_rank rank
extern playchar_t playchar;
#define registration_playchar playchar
extern unsigned char entered_place;
#define registration_place entered_place
extern unsigned char gALPHABET[51];
#define name_entry_alphabet gALPHABET

// Keep the historical external names above for the grouped SCORE_TEXT OMF.
// The registration body uses these aliases to state which cross-function
// values they carry; all aliases preprocess back to the same DGROUP symbols.
#define loaded_score_section hi

// MAINE score-registration immediates from the accepted body and 51-byte
// alphabet. Keep this scope separate from the unrelated MAIN rank system.
enum {
    STAGE_EXTRA = 6,
    RANK_EASY = 0,
    RANK_EXTRA = 4,
    SHOTTYPE_A = 0,
    ES_BAD = 0xFE,
    ES_GOOD = 0xFF,
    ALPHABET_ROWS = 3,
    ALPHABET_COLS = 17,
    ALPHABET_ENTER_ROW = ALPHABET_ROWS - 1,
    ALPHABET_ENTER_COL = ALPHABET_COLS - 1,
    NAME_REPEAT_DELAY_FRAMES = 30,
    SCOREDAT_NO_ENTRY = 0xFF,
};

extern "C" {
extern char aHi01_pi[];
extern char aScnum2_bft[];
extern char aGxgnbGvbGhvVGv[];
extern char aGxgnbGvbGhvV_1[];
extern char aName[];
}

bool pascal near hiscore_scoredat_load_for(playchar_t pc);
void near hiscore_scoredat_save(void);
void near score_insert(void);
void pascal near places_put(int rendered_playchar);
void pascal near alphabet_cursor_put(int col, int row, int color);
void pascal near name_cursor_put(
    int place, unsigned char rendered_playchar, unsigned char cursor
);

#if defined(TH04P)
#pragma codeseg SCORE_TEXT GROUP_01
#else
#pragma codeseg SCORE_TEXT score_01
#endif
#include "src/maine/score/regist_menu.inl"
#pragma codeseg

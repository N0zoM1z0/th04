// OP SCORE_TEXT high-score registration/view menu.
#include "src/shared/platform/types.hpp"
#include "src/shared/config/resident.hpp"
#include "src/shared/formats/pi.hpp"
#include "src/shared/hardware/frame_delay.hpp"
#include "src/shared/sound/api.hpp"

extern unsigned char rank;
extern unsigned short key_det;

void input_reset_sense(void);
bool near hiscore_scoredat_load_both(void);
void near rank_render(void);

enum {
    RANK_EASY = 0,
    RANK_EXTRA = 4,
    INPUT_NONE = 0,
    INPUT_LEFT = 0x0004,
    INPUT_RIGHT = 0x0008,
    INPUT_SHOT = 0x0020,
    INPUT_CANCEL = 0x1000,
    INPUT_OK = 0x2000,
};

#define BGM_HISCORE_FN "name"
#define BGM_MENU_MAIN_FN "op"
#define HISCORE_BG_FN "hi01.pi"
#define MENU_MAIN_BG_FN "op1.pi"

#pragma codeseg SCORE_TEXT op_01
#include "src/op/score/regist_view_menu.inl"
#pragma codeseg

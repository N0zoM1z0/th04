#include <process.h>

#include "src/shared/platform/types.hpp"
#include "src/shared/config/resident.hpp"
#include "src/shared/hardware/graphics.hpp"
#include "src/shared/sound/api.hpp"

static const int PLAYCHAR_REIMU = 0;

bool16 near playchar_menu(void);
void near main_cdg_free(void);
void near cfg_save(void);
void game_exit(void);

static char BINARY_MAIN[] = "main";
static char BINARY_DEB[] = "deb";

#pragma codeseg OP_MAIN_TEXT start_game_01
#include "src/op/start/start_game.inl"
#pragma codeseg

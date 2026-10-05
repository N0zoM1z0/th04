#include <process.h>

#include "src/shared/platform/types.hpp"
#ifdef TH04P
#include "src/shared/runtime/api.hpp"
#endif
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

// Keep the historical private data symbols while naming their roles at each
// use site. These aliases preprocess away and do not change the OMF surface.
#define GAMEPLAY_BINARY BINARY_MAIN
#define DEBUG_GAMEPLAY_BINARY BINARY_DEB

#ifdef TH04P
#pragma codeseg OP_NATIVE_TEXT OP_NATIVE_01
#else
#pragma codeseg OP_MAIN_TEXT start_game_01
#endif
#include "src/op/start/start_game.inl"
#pragma codeseg

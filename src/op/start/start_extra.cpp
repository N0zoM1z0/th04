#include <process.h>

#include "src/shared/platform/types.hpp"
#ifdef TH04P
#include "src/shared/runtime/api.hpp"
#endif
#include "src/shared/config/resident.hpp"
#include "src/shared/hardware/graphics.hpp"
#include "src/shared/sound/api.hpp"

static const int STAGE_EXTRA = 6;
static const int PLAYCHAR_REIMU = 0;

bool16 near playchar_menu(void);
void near main_cdg_free(void);
void near cfg_save(void);
void game_exit(void);

static char BINARY_MAIN[] = "main";
#define GAMEPLAY_BINARY BINARY_MAIN

#ifdef TH04P
#pragma codeseg OP_NATIVE_TEXT OP_NATIVE_01
#else
#pragma codeseg OP_MAIN_TEXT start_extra_01
#endif
#include "src/op/start/start_extra.inl"
#pragma codeseg

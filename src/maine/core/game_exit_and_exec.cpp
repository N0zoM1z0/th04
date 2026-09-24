#include <process.h>
#include <stddef.h>

extern "C" {
void far pascal cdg_free_all(void);
void far pascal graph_hide(void);
void far pascal text_clear(void);
int far pascal gaiji_restore(void);
}
void game_exit(void);

#pragma codeseg MAINE_E_TEXT maine_e_01
#include "src/maine/core/game_exit_and_exec.inl"
#pragma codeseg

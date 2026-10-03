#include <process.h>
#include <stddef.h>

extern "C" {
void far pascal cdg_free_all(void);
void far pascal graph_hide(void);
void far pascal text_clear(void);
int far pascal gaiji_restore(void);
}
void game_exit(void);

// Retain the attested parameter spelling in compiler output while exposing its
// process-handoff role in the included implementation.
#define next_program_fn fn

#if defined(TH04P)
#pragma codeseg MAINE_E_TEXT GROUP_01
#else
#pragma codeseg MAINE_E_TEXT maine_e_01
#endif
#include "src/maine/core/game_exit_and_exec.inl"
#pragma codeseg

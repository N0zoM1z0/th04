#ifndef TH04_DEMO_PREFIX_COMBINED
#pragma option -zCDEMO_TEXT -zPmain_01
#endif

#include "platform.h"
#include "src/shared/config/resident.hpp"
#include "src/shared/hardware/graphics.hpp"
#include "th04/snd/snd.h"
#include "th04/main/quit.hpp"

extern unsigned int mem_assign_paras;
extern long random_seed;

resident_t __seg* near cfg_load_resident_ptr(void);
int pascal game_init_main(const unsigned char *pf_fn);
void near ems_allocate_and_preload_eyecatch(void);
void near stage_session_init(void);
void near gameplay_loop(void);
extern "C" void near stage_session_free(void);
int pascal GameExecl(const char *binary_fn);
#pragma samecodeseg GameExecl
#define handoff_to_program GameExecl

extern const unsigned char main_pf_fn[];
extern const char gaiji_fn[];
extern const char se_fn[];
extern const char op_fn[];

void main(void)
{
	// MAIN is entered as a new DOS process. MIKO.CFG supplies the segment of the
	// ZUN.COM resident block that OP populated before replacing itself.
    if(!cfg_load_resident_ptr()) {
        return;
    }

    mem_assign_paras = (320000 >> 4);
    game_init_main(main_pf_fn);
	// Seed MAIN's process-local LCG from the menu-time accumulator. Every later
	// IRand() call, including ring fills and direct gameplay draws, advances this
	// state; ordinary stage changes do not copy the resident value again.
    random_seed = resident->rand;
    ems_allocate_and_preload_eyecatch();
    text_clear();
    gaiji_backup();
    gaiji_entry_bfnt(gaiji_fn);
    snd_determine_modes(resident->bgm_mode, resident->se_mode);
    snd_load(se_fn, SND_LOAD_SE);

	// A stage transition releases only stage-owned state and starts another
	// session in this process. Every other quit reason leaves the loop so the
	// complete process handoff below can publish statistics and free all state.
    for(;;) {
        stage_session_init();
        gameplay_loop();
        if(quit != Q_NEXT_STAGE) {
            break;
        }
        stage_session_free();
    }

	// Demo completion and non-ending exits return to a newly started OP.EXE.
	// Ending/game-over paths call the same handoff routine with MAINE instead.
	handoff_to_program(op_fn);
}

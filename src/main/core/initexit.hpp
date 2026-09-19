#ifndef TH04_MAIN_CORE_INITEXIT_HPP
#define TH04_MAIN_CORE_INITEXIT_HPP

#include <stddef.h>

int pascal game_init_main(const unsigned char *pf_fn);
void game_exit(void);
void game_exit_to_dos(void);
extern size_t mem_assign_paras;

#define graph_clear_both() \
	graph_accesspage(1); graph_clear(); \
	graph_accesspage(0); graph_clear(); \
	graph_accesspage(0); graph_showpage(0);

#endif

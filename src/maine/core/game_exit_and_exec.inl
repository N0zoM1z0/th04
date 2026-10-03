void pascal near game_exit_and_exec(char far *fn)
{
	// MAINE owns ending sprites, visible graphics/font state and the runtime
	// services started by game_init_main(). Release them before DOS overlays OP.
	cdg_free_all();
	graph_hide();
	text_clear();
	gaiji_restore();
	game_exit();
	// Successful execl() never returns; the original has no recovery path if
	// loading the menu executable fails after this teardown.
	execl(next_program_fn, next_program_fn, NULL);
}

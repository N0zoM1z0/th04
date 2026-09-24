void pascal near game_exit_and_exec(char far *fn)
{
	cdg_free_all();
	graph_hide();
	text_clear();
	gaiji_restore();
	game_exit();
	execl(fn, fn, NULL);
}

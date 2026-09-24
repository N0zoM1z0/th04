#pragma option -zCSHARED

void game_exit(void);

extern "C" {
void far pascal key_beep_on(void);
void far pascal text_systemline_show(void);
void far pascal text_cursor_show(void);
}

void game_exit_to_dos(void)
{
	game_exit();
	key_beep_on();
	text_systemline_show();
	text_cursor_show();
}

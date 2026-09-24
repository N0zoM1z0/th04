void pascal near se_choice_put(int se_mode, vc2 col)
{
	screen_y_t top = CHOICE_TOP;
	const shiftjis_t* str;
	switch(se_mode) {
	case SND_SE_FM:
		str = SE_CHOICE_FM;
		top += (0 * GLYPH_H);
		break;
	case SND_SE_BEEP:
		str = SE_CHOICE_BEEP;
		top += (1 * GLYPH_H);
		break;
	case SND_SE_OFF:
		str = SE_CHOICE_OFF;
		top += (2 * GLYPH_H);
		break;
	}
	graph_putsa_fx(CHOICE_LEFT, top, col, str);
}

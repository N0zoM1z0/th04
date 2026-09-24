void pascal near bgm_choice_put(int bgm_mode, vc2 col)
{
	screen_y_t top = CHOICE_TOP;
	const shiftjis_t* str;
	switch(bgm_mode) {
	case SND_BGM_FM86:
		str = BGM_CHOICE_FM86;
		top += (0 * GLYPH_H);
		break;
	case SND_BGM_FM26:
		str = BGM_CHOICE_FM26;
		top += (1 * GLYPH_H);
		break;
	case SND_BGM_OFF:
		str = BGM_CHOICE_OFF;
		top += (2 * GLYPH_H);
		break;
	}
	graph_putsa_fx(CHOICE_LEFT, top, col, str);
}

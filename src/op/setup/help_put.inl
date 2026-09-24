void near bgm_help_put(void)
{
	int top = HELP_TOP;
	for(int i = 0; i < HELP_LINES; (i++, top += GLYPH_H)) {
		graph_putsa_fx(HELP_LEFT, top, V_WHITE, BGM_HELP[i]);
	}
}

void near se_help_put(void)
{
	int top = HELP_TOP;
	for(int i = 0; i < HELP_LINES; (i++, top += GLYPH_H)) {
		graph_putsa_fx(HELP_LEFT, top, V_WHITE, SE_HELP[i]);
	}
}

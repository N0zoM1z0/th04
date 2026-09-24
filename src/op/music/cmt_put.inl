void near cmt_put(void)
{
	graph_putsa_fx(CMT_TITLE_LEFT, CMT_TITLE_TOP, COL_CMT_TRACK, cmt[0].c);
	for(int line = 1; line < CMT_LINES; line++) {
		if(cmt[line].c[0] == ';') {
			continue;
		}
		graph_putsa_fx(
			CMT_COMMENT_LEFT,
			((line + ((CMT_COMMENT_TOP - 1) / GLYPH_H)) * GLYPH_H),
			COL_CMT_COMMENT,
			cmt[line].c
		);
	}
}

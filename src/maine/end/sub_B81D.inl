void near sub_B81D(void)
{
	unsigned char digit;
	unsigned char past_leading_zeroes = 0;
	unsigned char g_str[SCORE_DIGITS + 1];
	register int i = 0;
	for(; i < SCORE_DIGITS; i++) {
		digit = resident->score_last.digits[(SCORE_DIGITS - 1) - i];
		past_leading_zeroes |= digit;
		if(past_leading_zeroes) {
			g_str[i] = (gb_0 + digit);
		} else {
			g_str[i] = g_EMPTY;
		}
	}
	g_str[SCORE_DIGITS] = g_NULL;
	graph_gaiji_puts(160, 96, GAIJI_W, g_str, 14);
	past_leading_zeroes = 1;
	graph_putsa_fx(288, 96, 14, aU_);
}

{
    int digit;
    pixel_t rel_left = 0x10;

    if((hi.score.g_score[place].digits[SCORE_DIGITS - 1] - 0xA0) >= 10) {
        super_put(
            0x8C, top,
            ((hi.score.g_score[place].digits[SCORE_DIGITS - 1] - 0xA0) / 10)
        );
    }
    if((hi2.score.g_score[place].digits[SCORE_DIGITS - 1] - 0xA0) >= 10) {
        super_put(
            0x1C0, top,
            ((hi2.score.g_score[place].digits[SCORE_DIGITS - 1] - 0xA0) / 10)
        );
    }
    super_put(
        0x9C, top,
        ((hi.score.g_score[place].digits[SCORE_DIGITS - 1] - 0xA0) % 10)
    );
    super_put(
        0x1D0, top,
        ((hi2.score.g_score[place].digits[SCORE_DIGITS - 1] - 0xA0) % 10)
    );

    digit = (SCORE_DIGITS - 2);
    while(digit >= 0) {
        super_put(
            (0x9C + rel_left), top,
            (hi.score.g_score[place].digits[digit] - 0xA0)
        );
        super_put(
            (0x1D0 + rel_left), top,
            (hi2.score.g_score[place].digits[digit] - 0xA0)
        );
        digit--;
        rel_left += 0x10;
    }
}

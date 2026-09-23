{
    enum {
        OP_SCORE_DIGIT_ZERO = 0xA0,
        OP_SCORE_DIGIT_ONE = 0xA1,
        OP_SCORE_NAME_DOT = 0xC4,
        OP_SCORE_NOT_CLEARED = 0x19,
        OP_SCORE_STAGE_BASE = 0xA5,
        OP_SCORE_INITIAL_DIGIT = 5
    };

    int i;
    int c;
    unsigned char digit = (OP_SCORE_DIGIT_ZERO + 10 - (10 / SCOREDAT_PLACES));

    for(i = 0; i < SCOREDAT_PLACES; i++) {
        hi.score.cleared = OP_SCORE_NOT_CLEARED;
        for(c = 0; c < SCORE_DIGITS; c++) {
            hi.score.g_score[i].digits[c] = OP_SCORE_DIGIT_ZERO;
        }

        if(i == 0) {
            hi.score.g_score[i].digits[OP_SCORE_INITIAL_DIGIT] = OP_SCORE_DIGIT_ONE;
        } else {
            hi.score.g_score[i].digits[OP_SCORE_INITIAL_DIGIT - 1] = digit;
            digit--;
        }

        hi.score.g_stage[i] = (OP_SCORE_STAGE_BASE - (i / 2));

        for(c = 0; c < SCOREDAT_NAME_LEN; c++) {
            hi.score.g_name[i][c] = OP_SCORE_NAME_DOT;
        }
        hi.score.g_name[i][SCOREDAT_NAME_LEN] = 0;
    }

    file_create("GENSOU.SCR");
    for(i = 0; i < SCOREDAT_PLACES; i++) {
        scoredat_encode();
        file_write(&hi, sizeof(hi));
        scoredat_decode();
    }
    file_close();
}

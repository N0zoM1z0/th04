{
    enum {
        MAINE_SCORE_NOT_CLEARED = 0x19,
        MAINE_SCORE_INITIAL_DIGIT = 5,
        MAINE_SCORE_NEXT_DIGIT = 4,
        MAINE_SCORE_STAGE_BASE = 0xA5
    };
    int i;
    int place;
    unsigned char digit = (gb_0 + 10 - (10 / SCOREDAT_PLACES));

    for(i = 0; i < SCOREDAT_PLACES; i++) {
        hi.score.cleared = MAINE_SCORE_NOT_CLEARED;
        for(place = 0; place < SCORE_DIGITS; place++) {
            hi.score.g_score[i].digits[place] = gb_0;
        }

        if(i == 0) {
            hi.score.g_score[i].digits[MAINE_SCORE_INITIAL_DIGIT] = gb_1;
        } else {
            hi.score.g_score[i].digits[MAINE_SCORE_NEXT_DIGIT] = digit;
            digit--;
        }

        hi.score.g_stage[i] = (MAINE_SCORE_STAGE_BASE - (i / 2));

        for(place = 0; place < SCOREDAT_NAME_LEN; place++) {
            hi.score.g_name[i][place] = gs_DOT;
        }
        hi.score.g_name[i][SCOREDAT_NAME_LEN] = 0;
    }

    // Preserve MAINE's linked DGROUP filename symbol instead of a header literal.
#ifdef SCOREDAT_FN
#undef SCOREDAT_FN
#endif
    extern const char SCOREDAT_FN[];
    file_create(SCOREDAT_FN);
    for(i = 0; i < SCOREDAT_PLACES; i++) {
        scoredat_encode();
        file_write(&hi, sizeof(hi));
        scoredat_decode();
    }
    file_close();
}

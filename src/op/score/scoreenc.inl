{
    int i;
    unsigned char feedback;

    hi.score_sum = 0;
    for(i = 4; i < sizeof(hi); i++) {
        hi.score_sum += ((unsigned char *)&hi)[i];
    }

    hi.key1 = irand();
    hi.key2 = irand();

    feedback = 0;
    for(i = (sizeof(hi) - 1); i >= offsetof(op_scoredat_section_t, score); i--) {
        ((unsigned char *)&hi)[i] -= (hi.key1 + feedback);
        feedback = ((unsigned char *)&hi)[i];
        feedback = _crotr(feedback, 3) ^ hi.key2;
    }
}

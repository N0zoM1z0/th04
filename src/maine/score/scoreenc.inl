{
    int i;
    unsigned char feedback;

    hi.score_sum = 0;
    for(i = offsetof(scoredat_section_t, score); i < sizeof(scoredat_section_t); i++) {
        hi.score_sum += ((unsigned char near *)&hi)[i];
    }

    hi.key1 = irand();
    hi.key2 = irand();

    feedback = 0;
    for(i = sizeof(scoredat_section_t) - 1;
            i >= offsetof(scoredat_section_t, score); i--) {
        ((unsigned char near *)&hi)[i] -= (unsigned char)hi.key1 + feedback;
        feedback = ((unsigned char near *)&hi)[i];
        feedback = (unsigned char)((feedback >> 3) | (feedback << 5));
        feedback ^= (unsigned char)hi.key2;
    }
}

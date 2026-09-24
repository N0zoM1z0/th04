{
    unsigned char feedback;
    register unsigned int sum;
    int i;

    for(i = offsetof(scoredat_section_t, score);
            i < sizeof(scoredat_section_t) - 1; i++) {
        feedback = ((unsigned char near *)&hi)[i + 1];
        feedback = (feedback >> 3) | (feedback << 5);
        feedback ^= (unsigned char)hi.key2;
        ((unsigned char near *)&hi)[i] =
                (unsigned char)hi.key1 + feedback + ((unsigned char near *)&hi)[i];
    }
    ((unsigned char near *)&hi)[i] += (unsigned char)hi.key1;

    sum = 0;
    for(i = offsetof(scoredat_section_t, score);
            i < sizeof(scoredat_section_t); i++) {
        sum += ((unsigned char near *)&hi)[i];
    }
    return (unsigned char)(hi.score_sum - sum);
}

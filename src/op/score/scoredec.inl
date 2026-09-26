#define OP_DECODE_SCOREDAT_SECTION(section, sum, i) \
    for((i) = offsetof(op_scoredat_section_t, score); \
            (i) < (sizeof(op_scoredat_section_t) - 1); (i)++) { \
        unsigned char tmp; \
        tmp = ((unsigned char *)&(section))[(i) + 1]; \
        _AL = (section).key2; \
        /* TC4J has no 8-bit rotate intrinsic; TH03 OP/MAINL independently corroborate this primitive. */ \
        asm { ror tmp, 3; } \
        tmp ^= _AL; \
        ((unsigned char *)&(section))[(i)] = \
                (section).key1 + tmp + ((unsigned char *)&(section))[(i)]; \
    } \
    ((unsigned char *)&(section))[(i)] += (section).key1; \
    (sum) = 0; \
    for((i) = offsetof(op_scoredat_section_t, score); \
            (i) < sizeof(op_scoredat_section_t); (i)++) { \
        (sum) += ((unsigned char *)&(section))[(i)]; \
    }

{
    int i;
    int sum;

    OP_DECODE_SCOREDAT_SECTION(hi, sum, i);
    if(hi.score_sum != sum) {
        return 1;
    }

    OP_DECODE_SCOREDAT_SECTION(hi2, sum, i);
    return hi2.score_sum - sum;
}

#undef OP_DECODE_SCOREDAT_SECTION

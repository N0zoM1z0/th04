#ifndef TH04_OP_SCOREDAT_HPP
#define TH04_OP_SCOREDAT_HPP

#include <stddef.h>
#include "src/shared/config/score.hpp"

// Both OP high-score columns use the same 196-byte section layout. Target
// accesses place the names at +4 and stages at +176 from each section base.
#define SCOREDAT_PLACES 10
#define SCOREDAT_NAME_LEN 8

struct op_scoredat_t {
    unsigned char g_name[SCOREDAT_PLACES][SCOREDAT_NAME_LEN + 1];
    score_lebcd_t g_score[SCOREDAT_PLACES];
    unsigned char cleared;
    unsigned char unused_1;
    unsigned char g_stage[SCOREDAT_PLACES];
    unsigned char unused_2[SCOREDAT_PLACES];
};

struct op_scoredat_section_t {
    signed char key1;
    signed char key2;
    short score_sum;
    op_scoredat_t score;
};

typedef char op_score_name_offset_check[(offsetof(op_scoredat_section_t, score.g_name) == 4) ? 1 : -1];
typedef char op_score_stage_offset_check[(offsetof(op_scoredat_section_t, score.g_stage) == 176) ? 1 : -1];
typedef char op_score_section_size_check[(sizeof(op_scoredat_section_t) == 196) ? 1 : -1];

extern op_scoredat_section_t hi;
extern op_scoredat_section_t hi2;

#endif

#ifndef TH04_MAINE_SCOREDAT_HPP
#define TH04_MAINE_SCOREDAT_HPP

#include <stddef.h>
#include "src/shared/config/score.hpp"

// MAINE's decoded SCORE_TEXT accesses these DGROUP fields at +4, +94, and
// +176 from hi. The 10-place, 8-digit layout is checked against the target.
#define SCOREDAT_PLACES 10
#define SCOREDAT_NAME_LEN 8

struct scoredat_t {
    unsigned char g_name[SCOREDAT_PLACES][SCOREDAT_NAME_LEN + 1];
    score_lebcd_t g_score[SCOREDAT_PLACES];
    unsigned char cleared;
    unsigned char unused_1;
    unsigned char g_stage[SCOREDAT_PLACES];
    unsigned char unused_2[SCOREDAT_PLACES];
};

struct scoredat_section_t {
    signed char key1;
    signed char key2;
    short score_sum;
    scoredat_t score;
};

typedef char maine_score_name_offset_check[(offsetof(scoredat_section_t, score.g_name) == 4) ? 1 : -1];
typedef char maine_score_digits_offset_check[(offsetof(scoredat_section_t, score.g_score) == 94) ? 1 : -1];
typedef char maine_score_stage_offset_check[(offsetof(scoredat_section_t, score.g_stage) == 176) ? 1 : -1];
typedef char maine_score_section_size_check[(sizeof(scoredat_section_t) == 196) ? 1 : -1];

extern scoredat_section_t hi;

// Target immediates in score_insert: gaiji digits A0/A1, dot C4, all E9,
// and the extra-ending threshold FD. These are TH04 symbols, not bytes copied
// into machine code or a reconstructed data array.
enum {
    gb_0 = 0xA0,
    gb_1 = 0xA1,
    gs_DOT = 0xC4,
    gs_ALL = 0xE9,
    ES_EXTRA = 0xFD,
};

#endif

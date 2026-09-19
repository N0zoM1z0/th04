#ifndef TH04_SCORE_H
#define TH04_SCORE_H

#define SCORE_DIGITS 8

typedef union {
    unsigned char continues_used;
    unsigned char digits[SCORE_DIGITS];
} score_lebcd_t;

extern score_lebcd_t score;

#endif

#ifndef TH04_MAIN_MATH_RANDRING_HPP
#define TH04_MAIN_MATH_RANDRING_HPP

#include "src/shared/platform/types.hpp"

// A stage fills this byte ring once from IRand(). Both the randring1_* and
// randring2_* entry-point families consume this same state; their numbering
// identifies two code-segment-local copies of the accessors, not two random
// streams. Calls through either family therefore affect every later caller.
//
// Each accessor reads a little-endian word beginning at randring[randring_p],
// then increments only the low byte of the word-sized cursor. Consecutive
// samples normally overlap by one byte. At cursor 255, the word read crosses
// the array boundary into the immediately following low byte of randring_p,
// which is 0xFF before that call increments it back to 0. This wrap sample is
// part of the original sequence and must remain intact in the exact product.
#define RANDRING_SIZE 256

extern uint8_t randring[RANDRING_SIZE];
extern uint16_t randring_p;

void near randring_fill(void);

uint16_t near randring1_next16(void);
uint16_t pascal near randring1_next16_and(uint16_t mask);
uint16_t pascal near randring1_next16_mod(uint16_t divisor);

uint16_t near randring2_next16(void);
uint16_t pascal near randring2_next16_and(uint16_t mask);
uint16_t pascal near randring2_next16_mod(uint16_t divisor);

inline uint8_t randring1_next8_ge_lt(uint8_t min, uint8_t max) {
	// This mask form produces [min, max) only when (max - min) is a
	// nonzero power of two. The sole TH04 caller uses a width of 0x10.
	return (min + randring1_next16_and((max - min) - 1));
}

#endif

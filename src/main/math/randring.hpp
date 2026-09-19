#ifndef TH04_MAIN_MATH_RANDRING_HPP
#define TH04_MAIN_MATH_RANDRING_HPP

#include "src/shared/platform/types.hpp"

// TH04's two consumers share one 256-byte random ring and a word-sized cursor.
// The original routines advance only the low byte of that cursor.
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
	return (min + randring1_next16_and((max - min) - 1));
}

#endif

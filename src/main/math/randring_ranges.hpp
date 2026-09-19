#ifndef TH04_MAIN_MATH_RANDRING_RANGES_HPP
#define TH04_MAIN_MATH_RANDRING_RANGES_HPP

#include "src/main/math/randring.hpp"

// Include this after the owning gameplay header that defines subpixel_t and
// to_sp8(). Only bullet addition uses this source-level convenience helper.
template <class T> inline bool is_range_a_power_of_two(T min, T max) {
	return (((max - min) & ((max - min) - 1)) == 0);
}

inline uint8_t randring2_next8_and_ge_lt(uint8_t min, uint8_t max) {
	return (min + randring2_next16_and((max - min) - 1));
}

inline subpixel_t randring2_next8_ge_lt_sp(float min, float max) {
	return randring2_next8_and_ge_lt(to_sp8(min), to_sp8(max));
}

inline int16_t randring2_next16_mod_ge_lt(int16_t min, int16_t max) {
	return (min + randring2_next16_mod(max - min));
}

inline int16_t randring2_next16_ge_lt(int16_t min, int16_t max) {
	if(is_range_a_power_of_two(min, max)) {
		return (min + randring2_next16_and((max - min) - 1));
	}
	return randring2_next16_mod_ge_lt(min, max);
}

#endif

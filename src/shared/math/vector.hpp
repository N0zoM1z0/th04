#ifndef TH04_SHARED_MATH_VECTOR_HPP
#define TH04_SHARED_MATH_VECTOR_HPP

#include "src/shared/platform/abi.hpp"

typedef int vector_subpixel_t;

// Target-observed vector2_at ABI: a near reference to two adjacent 16-bit
// output coordinates. This deliberately does not claim the full SPPoint API.
struct vector2_at_result_t {
	vector_subpixel_t x;
	vector_subpixel_t y;
};

extern "C" {
void pascal vector2_at(
	vector2_at_result_t near &ret,
	vector_subpixel_t origin_x,
	vector_subpixel_t origin_y,
	vector_subpixel_t length,
	int angle
);
}

#endif

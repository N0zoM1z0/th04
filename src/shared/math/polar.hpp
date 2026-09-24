#ifndef TH04_SHARED_MATH_POLAR_HPP
#define TH04_SHARED_MATH_POLAR_HPP

#include "src/shared/runtime/api.hpp"
#include "src/shared/platform/pc98.hpp"

int pascal polar(int center, int radius, int ratio);

#define polar_by_offset(center, radius, table, offset) ( \
	(static_cast<long>(radius) * *reinterpret_cast<const short *>( \
		reinterpret_cast<const int8_t*>(table) + offset \
	) >> 8) + center \
)

static inline pixel_t polar_x_fast_unsafe(
	pixel_t center, pixel_t &radius, uint16_t table_offset
) {
	return polar_by_offset(center, radius, CosTable8, table_offset);
}

static inline pixel_t polar_y_fast_unsafe(
	pixel_t center, pixel_t &radius, uint16_t table_offset
) {
	return polar_by_offset(center, radius, SinTable8, table_offset);
}

#endif

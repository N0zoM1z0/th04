#pragma option -zCSHARED

#include "src/shared/math/polar.hpp"
#include "src/shared/math/vector.hpp"

int pascal polar(int center, int radius, int ratio)
{
	return (((static_cast<long>(radius) * ratio) >> 8) + center);
}

void pascal vector2_at(
	vector2_at_result_t near &ret,
	vector_subpixel_t origin_x,
	vector_subpixel_t origin_y,
	vector_subpixel_t length,
	int angle
)
{
	_BX = angle;
#if (GAME == 5)
	_BH ^= _BH;
#endif
	_BX += _BX; // *= sizeof(short)
	ret.x = polar_x_fast_unsafe(origin_x, length, _BX);
	ret.y = polar_y_fast_unsafe(origin_y, length, _BX);
}

#ifndef TH01_MATH_SUBPIXEL_HPP
#define TH01_MATH_SUBPIXEL_HPP

#include "src/shared/platform/pc98.hpp"

#define PIXEL_NONE (-999)

typedef uint8_t subpixel_length_8_t;
typedef int subpixel_t;

static const subpixel_t SUBPIXEL_FACTOR = 16;
static const char SUBPIXEL_BITS = 4;

#define TO_SP(v) ((v) << SUBPIXEL_BITS)
#define TO_PIXEL(v) ((v) >> SUBPIXEL_BITS)
#define TO_PIXEL_INPLACE(v) ((v) >>= SUBPIXEL_BITS)
#define TO_SP_INPLACE(v) ((v) <<= SUBPIXEL_BITS)

inline subpixel_t to_sp(float pixel_v)
{
	return static_cast<subpixel_t>(pixel_v * SUBPIXEL_FACTOR);
}

inline subpixel_length_8_t to_sp8(float pixel_v)
{
	return static_cast<subpixel_length_8_t>(to_sp(pixel_v));
}

template <class SubpixelType, class PixelType> class SubpixelBase {
public:
	typedef SubpixelBase<SubpixelType, PixelType> SelfType;

	SubpixelType v;

	SubpixelType operator +(float pixel_v) const {
		return (this->v + static_cast<SubpixelType>(to_sp(pixel_v)));
	}

	SubpixelType operator -(const SelfType &other) const {
		return (this->v - other.v);
	}

	void operator +=(float pixel_v) {
		this->v += static_cast<SubpixelType>(to_sp(pixel_v));
	}

	void operator -=(float pixel_v) {
		this->v -= static_cast<SubpixelType>(to_sp(pixel_v));
	}

	void set(float pixel_v) {
		v = static_cast<SubpixelType>(to_sp(pixel_v));
	}

	void set(const PixelType &pixel_v) {
		v = static_cast<SubpixelType>(TO_SP(pixel_v));
	}

	PixelType to_pixel() const {
		return static_cast<PixelType>(TO_PIXEL(v));
	}

	PixelType to_pixel_slow() const {
		return (v / 16);
	}

	operator SubpixelType() const {
		return v;
	}

	static SubpixelType None() {
		return static_cast<SubpixelType>(TO_SP(PIXEL_NONE));
	}
};

template <class T> struct SPPointBase {
	T x, y;

	void set(float screen_x, float screen_y) {
		x.set(screen_x);
		y.set(screen_y);
	}
};

typedef SubpixelBase<subpixel_t, pixel_t> Subpixel;

struct SPPoint : public SPPointBase<Subpixel> {
	void set_long(subpixel_t subpixel_x, subpixel_t subpixel_y) {
		reinterpret_cast<uint32_t &>(x) = (
			subpixel_x | (static_cast<uint32_t>(subpixel_y) << 16)
		);
	}
};

typedef SubpixelBase<subpixel_length_8_t, pixel_length_8_t> SubpixelLength8;
typedef SubpixelBase<char, pixel_delta_8_t> Subpixel8;
typedef SPPointBase<Subpixel8> SPPoint8;

#endif

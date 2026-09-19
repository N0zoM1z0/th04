#ifndef TH04_MAIN_MATH_POLAR_HPP
#define TH04_MAIN_MATH_POLAR_HPP

int pascal polar(int center, int radius, int ratio);

#define polar_x(center, radius, angle) polar(center, radius, CosTable8[angle])
#define polar_y(center, radius, angle) polar(center, radius, SinTable8[angle])

#endif

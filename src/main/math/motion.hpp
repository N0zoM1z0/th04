#ifndef TH04_MAIN_MATH_MOTION_HPP
#define TH04_MAIN_MATH_MOTION_HPP

template <class PointType> struct near MotionBase {
	PointType cur;
	PointType prev;
	PointType velocity;

	void init(float screen_x, float screen_y) {
		cur.x.set(screen_x);
		prev.x.set(screen_x);
		cur.y.set(screen_y);
		prev.y.set(screen_y);
	}
};

#endif

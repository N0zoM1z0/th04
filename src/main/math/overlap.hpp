#ifndef TH04_MAIN_MATH_OVERLAP_HPP
#define TH04_MAIN_MATH_OVERLAP_HPP

// Collision predicates used by TH04 MAIN.EXE. These preserve the argument
// evaluation order and in-place delta updates of the original macros.
#define overlap_offcenter_1d_inplace_fast(delta, dist_edge1, dist_edge2) ( \
	(unsigned int)((delta) += dist_edge1, delta) <= (dist_edge1 + dist_edge2) \
)

#define overlap_offcenter_inplace_fast( \
	delta_x, delta_y, dist_to_left, dist_to_top, dist_to_right, dist_to_bottom \
) ( \
	overlap_offcenter_1d_inplace_fast(delta_x, dist_to_left, dist_to_right) && \
	overlap_offcenter_1d_inplace_fast(delta_y, dist_to_top, dist_to_bottom) \
)

#define overlap_1d_inplace_fast(delta, extent) ( \
	(unsigned int)((delta) += (extent / 2), delta) <= (extent) \
)

#define overlap_wh_inplace_fast(delta_x, delta_y, w, h) ( \
	overlap_1d_inplace_fast(delta_x, w) && \
	overlap_1d_inplace_fast(delta_y, h) \
)

#define overlap_points_wh_fast(p1, p2, p1_w, p1_h) ( \
	((unsigned int)((p1.x - p2.x) + (p1_w / 2)) <= (p1_w)) && \
	((unsigned int)((p1.y - p2.y) + (p1_h / 2)) <= (p1_h)) \
)

#endif

#ifndef TH04_MAIN_BULLET_ADD_IMPL_HPP
#define TH04_MAIN_BULLET_ADD_IMPL_HPP

#define bullet_group_ring_impl(angle_offset, group_complete, i, count, aim_or_no_aim) { \
	angle_offset = ((GAME >= 3) \
		? ((i * BULLET_ANGLE_FULL_TURN) / count) \
		: (i * (BULLET_ANGLE_FULL_TURN / count))); \
	if(i >= (count - 1)) { \
		group_complete = true; \
	} \
	goto aim_or_no_aim; \
}

#endif

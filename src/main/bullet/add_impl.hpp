#ifndef TH04_MAIN_BULLET_ADD_IMPL_HPP
#define TH04_MAIN_BULLET_ADD_IMPL_HPP

#define bullet_group_ring_impl(i_angle, done, i, count, aim_or_no_aim) { \
	i_angle = ((GAME >= 3) ? ((i * 0x100) / count) : (i * (0x100 / count))); \
	if(i >= (count - 1)) { \
		done = true; \
	} \
	goto aim_or_no_aim; \
}

#endif

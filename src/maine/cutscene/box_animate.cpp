#include "src/shared/hardware/frame_delay.hpp"

// The reviewed body tests this target global through an 8-bit memory operand.
extern unsigned char fast_forward;
extern int text_interval;

typedef enum {
	BOX_MASK_0 = 0,
	BOX_MASK_1,
	BOX_MASK_2,
	BOX_MASK_3,
	BOX_MASK_COPY,
	box_mask_t_force_uint16 = 0xFFFF
} box_mask_t;

void near egc_start_copy(void);
void pascal near box_1_to_0_masked(box_mask_t mask);
void far egc_off(void);

#pragma codeseg CUTSCENE_TEXT cutscene_01
#include "src/maine/cutscene/box_animate.inl"
#pragma codeseg

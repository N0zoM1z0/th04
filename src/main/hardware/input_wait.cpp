#pragma option -zCSHARED

#include "src/shared/hardware/frame_delay.hpp"
#include "th04/hardware/input.h"

void pascal input_wait_for_change(int press_timeout_frames)
{
	enum { REPEATING_PRESS_WAIT = 9999 };
	int elapsed_press_frames = 0;

	// Release has no timeout and always samples after at least one frame.
	// Reset each sample because input_sense() ORs into the detection word.
	// Reset samples before the frame; sense accumulates after it. Both
	// observations must be clear for the release phase to finish.
	do {
		input_reset_sense();
		frame_delay(1);
		input_sense();
	} while(key_det != INPUT_NONE);

	// Zero and an explicit 9999 both select a repeating, unbounded press wait.
	if(!press_timeout_frames) {
		press_timeout_frames = REPEATING_PRESS_WAIT;
	}

	// The budget starts after release. Negative budgets skip the press phase.
	while(elapsed_press_frames < press_timeout_frames) {
		input_reset_sense();
		frame_delay(1);
		input_sense();
		if(key_det != INPUT_NONE) {
			break;
		}
		elapsed_press_frames++;
		if(press_timeout_frames == REPEATING_PRESS_WAIT) {
			elapsed_press_frames = 0;
		}
	}
}

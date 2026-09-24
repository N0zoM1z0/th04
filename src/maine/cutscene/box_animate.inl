// Natural C++ hypothesis for the target-reviewed 1A05:07C5 helper.
// The source-derived name is a candidate label, not a target-attested symbol.
void near box_1_to_0_animate(void)
{
	egc_start_copy();
	if(!fast_forward) {
		for(int mask = BOX_MASK_0; mask < BOX_MASK_COPY; mask++) {
			box_1_to_0_masked(static_cast<box_mask_t>(mask));
			frame_delay(text_interval);
		}
	}
	box_1_to_0_masked(BOX_MASK_COPY);
	egc_off();
}

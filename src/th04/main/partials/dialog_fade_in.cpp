void near dialog_box_fade_in_animate(void)
{
	vsync_Count1 = 0; // ZUN bloat: Automatically done in frame_delay().
	for(int i = 0; i < BOX_TILE_COUNT; i++) {
		dialog_box_put(BOX_BOSS_LEFT, BOX_BOSS_TOP, i);
		dialog_box_put(BOX_PLAYCHAR_LEFT, BOX_PLAYCHAR_TOP, i);
		frame_delay(12);
	}
}

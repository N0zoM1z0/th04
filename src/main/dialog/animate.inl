void dialog_animate(void)
{
	dialog_init();
	dialog_pre();
	dialog_run();

	#pragma samecodeseg tiles_activate_and_render_all_for_next_N_frames
	tiles_activate_and_render_all_for_next_N_frames(PAGE_COUNT);

	dialog_exit();
	dialog_post();
}

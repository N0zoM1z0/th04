void near box_bg_free(void)
{
	if(box_bg) {
		hmem_free(reinterpret_cast<void __seg *>(box_bg));
		box_bg = 0;
	}
}

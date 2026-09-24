void near raise_bg_free(void)
{
	hmem_free(reinterpret_cast<void __seg *>(raise_bg[0]));
	hmem_free(reinterpret_cast<void __seg *>(raise_bg[1]));
}

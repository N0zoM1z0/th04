void near nopoly_B_snap(void)
{
	nopoly_B = static_cast<unsigned char __seg *>(hmem_allocbyte(0x7D00));
	for(int p = 0; p < 0x7D00; p += 4) {
		*reinterpret_cast<unsigned long far *>(nopoly_B + p) =
			*reinterpret_cast<unsigned long far *>(VRAM_PLANE_B + p);
	}
}

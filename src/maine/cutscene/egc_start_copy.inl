void near egc_start_copy(void)
{
	egc_on();
	outport(EGC_ACTIVEPLANEREG, 0xFFF0);
	outport(EGC_READPLANEREG, 0x00FF);
	outport(EGC_MODE_ROP_REG, 0x3100);
	outport(EGC_MASKREG, 0xFFFF);
	outport(EGC_ADDRRESSREG, 0);
	outport(EGC_BITLENGTHREG, 0x000F);
}

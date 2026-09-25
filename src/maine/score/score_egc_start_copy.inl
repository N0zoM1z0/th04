void near score_egc_start_copy(void)
{
	_outportb_(0x7C, 0);
	_outportb_(0x6A, 7);
	_outportb_(0x6A, 5);
	_outportb_(0x7C, 0x80);
	_outportb_(0x6A, 6);
	_AX = 0xFFF0; _DX = EGC_ACTIVEPLANEREG; outport(_DX, _AX);
	_AX = 0x00FF; _DX = EGC_READPLANEREG; outport(_DX, _AX);
	_AX = 0x3100; _DX = EGC_MODE_ROP_REG; outport(_DX, _AX);
	_AX = 0xFFFF; _DX = EGC_MASKREG; outport(_DX, _AX);
	_AX = keep_0(0); _DX = EGC_ADDRRESSREG; outport(_DX, _AX);
	_AX = 0x000F; _DX = EGC_BITLENGTHREG; outport(_DX, _AX);
}

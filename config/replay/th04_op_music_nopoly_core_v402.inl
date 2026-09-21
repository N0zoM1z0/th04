	asm { xor di, di; xor si, si; }
	_CX = (PLANE_SIZE / 2);
	asm { rep movsw; }

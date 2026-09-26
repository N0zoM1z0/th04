// Maintained hybrid reconstruction of the Music Room B-plane restore.
//
// TH03, TH04, and TH05 OP release targets preserve this complete 30-byte
// function modulo only the linked _nopoly_B address. Keep ordinary TC4J
// pseudoregister loads for segment values and copy length; retain only the
// segment-save, zero-register encoding, and REP MOVSW primitive symbolically.
//
// No emitted opcode bytes, target byte arrays, or post-build patches.
void near nopoly_B_put(void)
{
	asm { push ds; }

	_AX = SEG_PLANE_B;
	_ES = _AX;
	_AX = (unsigned int)nopoly_B;
	_DS = _AX;

	// Ordinary TC4J "reg = 0" selects XOR r16,r/m16 (33 /r). All three
	// release targets use the equally valid XOR r/m16,r16 form (31 /r).
	asm {
		xor di, di
		xor si, si
	}

	_CX = (PLANE_SIZE / sizeof(unsigned short));

	// The copy is a hardware-facing segment/string primitive. The complete
	// PUSH DS ... REP MOVSW ... POP DS shape is shared by TH03/TH04/TH05.
	asm {
		rep movsw
		pop ds
	}
}

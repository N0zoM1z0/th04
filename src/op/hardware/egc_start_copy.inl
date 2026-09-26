// Maintained hybrid reconstruction of TH04 OP's internal EGC copy setup.
//
// TH04 OP and independently attested TH05 OP/MAINE targets preserve this
// complete 63-byte helper byte-for-byte. Keep ordinary EGC word-register writes
// in C++; retain only the cross-game-corroborated low-level PC-98 primitives
// symbolically.
//
// No emitted opcode arrays, codestrings, or post-build patches.
static void near egc_start_copy(void)
{
	// GRCG TDW mode + BIOS 0000:0495 shadow update, preserving FLAGS and ES,
	// followed by the immediate-port EGC enable sequence.
	asm {
		push es
		push 0
		pop es
		pushf
		cli
		mov al, GC_TDW
		out 0x7C, al
		mov byte ptr es:[0x495], al
		popf
		pop es

		mov al, 0x07
		out 0x6A, al
		mov al, 0x05
		out 0x6A, al
		mov al, 0x06
		out 0x6A, al
	}

	outport(EGC_ACTIVEPLANEREG, 0xFFF0);
	outport(EGC_READPLANEREG, 0x00FF);
	outport(EGC_MASKREG, 0xFFFF);

	// TC4J's register-expression lowering emits the target MOV DX,04ACh /
	// SUB AX,AX / OUT DX,AX sequence. Ordinary literal/local-zero forms select
	// different encodings; all three target artifacts above corroborate this
	// exact low-level primitive.
	_DX = EGC_ADDRRESSREG;
	_AX -= _AX;
	outport(_DX, _AX);

	outport(EGC_BITLENGTHREG, 0xF);
}

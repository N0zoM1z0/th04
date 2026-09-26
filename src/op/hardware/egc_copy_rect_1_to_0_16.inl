// Maintained hybrid reconstruction of TH04 OP's EGC page-1-to-page-0
// rectangle copier.
//
// TH05 OP and MAINE independently preserve the same parameter/register
// allocation and rectangle arithmetic, adding only their out-of-range guard.
// Keep those ordinary arithmetic/control-flow parts in C++. Retain only
// irreducible x86/PC-98 primitives symbolically; do not emit opcode bytes.
void DEFCONV egc_copy_rect_1_to_0_16(
	screen_x_t left, vram_y_t top, pixel_t w, pixel_t h
)
{
	#define vo_tmp	_BX // vram_offset_t
	#define first_bit	_CX
	#define stride	static_cast<vram_byte_amount_t>(_BP)
	#define w_tmp	static_cast<vram_word_amount_t>(_AX)
	#define rows_remaining	static_cast<pixel_t>(_BX)
	#define dots	static_cast<dots16_t>(_DX)

	// TH04's forward string-store loop requires DF=0.
	asm { cld; }
	egc_start_copy();

	outport(EGC_MODE_ROP_REG, 0x29F0);

	// Ordinary TC4J pseudoregister assignments emit the target BP-relative
	// parameter loads; inline assembly is not required here.
	_AX = left;
	_DX = top;

	vo_tmp = _AX;
	static_cast<vram_offset_t>(vo_tmp) >>= EGC_REGISTER_BITS;

	// TC4J lowers the ordinary <<= 1 form to ADD reg,reg. The target and both
	// TH05 descendants use SHL reg,1, so keep these two shifts symbolic.
	asm { shl bx, 1; }

	_DX <<= 6;
	vo_tmp += _DX;
	_DX >>= 2;
	vo_tmp += _DX;

	_DI = vo_tmp;
	_AX &= EGC_REGISTER_MASK;
	first_bit = _AX;

	w_tmp = ((_AX + w) >> EGC_REGISTER_BITS);
	if(first_bit) {
		w_tmp++;
	}
	egcrect_w = w_tmp;

	_CX = (ROW_SIZE / EGC_REGISTER_SIZE);
	_CX -= w_tmp;
	asm { shl cx, 1; }

	rows_remaining = h;
	stride = _CX;
	_ES = SEG_PLANE_B;

	do {
		_CX = egcrect_w;
		put_loop: {
			// Immediate-port page selection is stable in TH03/TH04/TH05
			// release code. TC4J's ordinary outportb() surface uses DX and
			// therefore does not reproduce this form.
			_AL = 1;
			asm { out 0xA6, al; }
			dots = peek(_ES, _DI);

			_AX ^= _AX;
			asm { out 0xA6, al; }

			// Forward STOSW plus LOOP is the TH04 specialization of the
			// cross-game page-copy loop. MOV AX,DX / STOSW and LOOP have
			// independent release-target lineage across TH02-TH05.
			_AX = dots;
			asm { stosw; loop put_loop; }
		}
		_DI += stride;
		rows_remaining--;
	} while(!FLAGS_SIGN);

	egc_off();

	#undef dots
	#undef rows_remaining
	#undef w_tmp
	#undef stride
	#undef first_bit
	#undef vo_tmp
}

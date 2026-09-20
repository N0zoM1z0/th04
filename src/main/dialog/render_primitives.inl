void pascal near dialog_box_put(uscreen_x_t left, uvram_y_t top, int tile)
{
	#define rows_left	static_cast<pixel_t>(_DX)

	// ZUN bloat: A near pointer would have been much simpler...
	#define offset	static_cast<uint16_t>(_BX)

	grcg_setcolor(GC_RMW, 1);
	_ES = SEG_PLANE_B;
	_AX = left;
	_DX = top;
	_AX >>= 3;
	_DX <<= 6;
	asm { add ax, dx; }
	_DX >>= 2;
	asm { add ax, dx; }
	asm { mov di, ax; }

	static_assert(BOX_TILE_SIZE == 8);
	offset = tile;
	offset <<= 3;

	rows_left = BOX_H;

	do {
		static_assert(BOX_TILE_VRAM_W == 2);
		static_assert((BOX_VRAM_W & 1) == 0);
		_CX = (BOX_VRAM_W / 2);
		_AX = *reinterpret_cast<const dots_t(BOX_TILE_W) __ds *>(
			(reinterpret_cast<const uint8_t __ds *>(BOX_TILES) + offset)
		);
		asm { rep stosw };

		// A needlessly clever wraparound check that expects the box tile size
		// to be a power of two.
		static_assert((BOX_TILE_SIZE & (BOX_TILE_SIZE - 1)) == 0);
		offset += BOX_TILE_VRAM_W;

		// Turbo C++ is too smart to emit this instruction with
		// pseudo-registers, turning it into `TEST BL, 7`.
		asm { test bx, (BOX_TILE_SIZE - 1); }
		if(FLAGS_ZERO) {
			offset -= BOX_TILE_SIZE;
		}

		_DI += (ROW_SIZE - BOX_VRAM_W);
	} while(--rows_left);

	grcg_off();

	#undef offset
	#undef rows_left
}

#define egc_rect_interpage_16(bottom_p, w, src_page) { \
	_DX = 0xA6; /* PC-98 VRAM page access port */ \
	_AL = src_page; \
	\
	do { \
		_CX = (w / EGC_REGISTER_DOTS); \
		word_loop: { \
			outportb(_DX, _AL); _AL ^= 1; _BX = *bottom_p; \
			outportb(_DX, _AL); _AL ^= 1; *bottom_p = _BX; \
			bottom_p++; \
			asm { loop word_loop; } \
		} \
	} while(((int16_t)(bottom_p) -= ((RES_X + w) / BYTE_DOTS)) >= 0); \
}

void near playfield_copy_front_to_back(void)
{
	egc_start_copy_noframe();
	_ES = grcg_segment(0, PLAYFIELD_TOP);
	_DI = (((PLAYFIELD_H - 1) * ROW_SIZE) + PLAYFIELD_VRAM_LEFT);
	egc_rect_interpage_16(
		reinterpret_cast<egc_temp_t __es *>(_DI), PLAYFIELD_W, page_front
	);

	// The above call returns the VRAM page access port in DX, [page_front] in
	// AL, and ![page_front] as the accessed page. Since the caller expects to
	// access the other one, we should switch back here, and this single-byte
	// instruction is all it takes as a result.
	// (Technically, it's not necessary since the accessed page only matters
	// for face blitting and dialog_face_unput_8()'s back→front copy will
	// override the accessed page anyway, but it's still good form. Kudos to
	// ZUN for doing the correct thing for once!)
	outportb(_DX, _AL);

	egc_off();
}

void pascal near dialog_face_unput_8(uscreen_x_t left, uvram_y_t top)
{
	egc_start_copy_noframe();

	// ZUN bloat: _ES = grcg_segment(0, top);
	_AX = top;
	asm { mov bx, ax; }
	_AX <<= 2;
	asm { add ax, bx; }
	_AX += SEG_PLANE_B;
	_ES = _AX;

	_DI = ((FACE_H - 1) * ROW_SIZE);
	_AX = left;
	_AX >>= 3;
	asm { add di, ax; }
	egc_rect_interpage_16(
		reinterpret_cast<egc_temp_t __es *>(_DI), FACE_W, page_back
	);
	egc_off();
}

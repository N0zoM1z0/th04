void pascal near carpet_lighting_put_new(int cel, unsigned int target_level)
{
	#define _SI               	reinterpret_cast<uint8_t near *>(_SI)
	#define tile_image_vos    	reinterpret_cast<vram_offset_t __ds *>(_BX)
	#define tile_ring_bytewise	reinterpret_cast<uint8_t __ds*>(tile_ring)

	// The remaining low-level operations form one coherent TC4J integrated-
	// assembler producer fingerprint (v420). Keep them symbolic; the ordinary
	// C++ statements around them remain natural TC4J source.
	asm {
		push ds;
		pop es;
	}

	_BX = TILES_X;
	_AX = cel;
	asm {
		mul bx;
		mov si, ax;
	}
	_SI += FP_OFF(CARPET_LIGHTING_ANIM);

	_AX = target_level;
	static_assert(
		sizeof(CARPET_TILE_IMAGE_VOS[0][0]) ==
		(2 * sizeof(CARPET_LIGHTING_ANIM[0][0]))
	);
	asm {
		add bx, bx;
		mul bx;
	}
	_AX += FP_OFF(CARPET_TILE_IMAGE_VOS);
	asm {
		mov bx, ax;
		xor dx, dx;
	}

	_CX = TILES_X;
	column_loop: {
		asm { lodsb; }
		if(_AL == 1) {
			asm {
				mov di, dx;
				shl di, 1;
			}
			_AX = *tile_image_vos;
			do {
				*reinterpret_cast<vram_offset_t near *>(
					&tile_ring_bytewise[_DI]
				) = _AX;
				_DI += sizeof(tile_ring[0]);
			} while(_DI < sizeof(tile_ring));

			asm { mov di, dx; }
			do {
				halftiles_dirty[0][_DI] = true;
				_DI += sizeof(halftiles_dirty[0]);
			} while(_DI < sizeof(halftiles_dirty));
		}
		_DX++;
		tile_image_vos++;
		asm { loop column_loop; }
	}

	#undef tile_ring_bytewise
	#undef tile_image_vos
	#undef _SI
}

			_AX = *tile_image_vos;
			do {
				*reinterpret_cast<vram_offset_t near *>(
					&tile_ring_bytewise[_DI]
				) = _AX;
				_DI += sizeof(tile_ring[0]);
			} while(_DI < sizeof(tile_ring));

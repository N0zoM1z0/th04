			do {
				halftiles_dirty[0][_DI] = true;
				_DI += sizeof(halftiles_dirty[0]);
			} while(_DI < sizeof(halftiles_dirty));
			/// -------------------------------
		}
		tile_x++;
		tile_image_vos++;

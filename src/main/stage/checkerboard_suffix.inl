				} while((vram_off -= (ROW_SIZE + PLAYFIELD_VRAM_W)) >= 0);

				// Move [vram_seg] to the next column and row, and continue if
				// we haven't reached the top of the playfield yet.
				checkerboard_vo_x_flip(vo_x);
				vram_seg -= ((CHECKERBOARD_H * ROW_SIZE) / 16);
			} while(vram_seg > grcg_segment_(0, PLAYFIELD_TOP));

			// If we came here from the top row, [vram_seg] is in fact exactly
			// equal to this value. Otherwise, jump there.
		} while(vram_seg != grcg_segment_(0, (PLAYFIELD_TOP - CHECKERBOARD_H)));

		loops--;
		if(FLAGS_ZERO) {
			break;
		}

		grcg_setcolor_direct_constant(1);
		vo_x = checkerboard.u1.var.vo_x_of_dark;
		checkerboard_vo_x_flip(vo_x);
	}

	checkerboard.seg_bottom -= (CHECKERBOARD_VO_SPEED / 16);
	checkerboard.off_bottom += CHECKERBOARD_VO_SPEED;
	if(checkerboard.seg_bottom < grcg_segment_(
		0, (PLAYFIELD_BOTTOM - CHECKERBOARD_H)
	)) {
		// The bottom row would be (CHECKERBOARD_H + CHECKERBOARD_SPEED) pixels
		// high on the next frame, which means that we've fully scrolled the
		// bottommost square onto the playfield during this frame. Start the
		// new frame at the CHECKERBOARD_SPEED offset, and flip the colors
		// accordingly.
		checkerboard.seg_bottom = grcg_segment(
			0, (PLAYFIELD_BOTTOM - CHECKERBOARD_SPEED)
		);
		checkerboard.off_bottom = CHECKERBOARD_VO_SPEED;
		checkerboard_vo_x_flip(checkerboard.u1.var.vo_x_of_dark);
	}
	checkerboard.off_top -= CHECKERBOARD_VO_SPEED;
	if(FLAGS_SIGN) {
		// Scrolled the top row off the playfield, so we start a new one at the
		// bottom of a full square in the next frame. No color flip necessary
		// here, since we render from bottom to top. (There's also always a
		// half-scrolled square at the bottom whenever we get here.)
		checkerboard.off_top = ((CHECKERBOARD_H - 1) * ROW_SIZE);
	}

	#undef vram_seg
	#undef vram_off
	#undef vo_x
	#undef loops
	#undef loops_and_vo_x
}

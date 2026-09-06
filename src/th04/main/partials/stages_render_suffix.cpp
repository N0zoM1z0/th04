void pascal near stage4_render(void)
{
	#define lighting_cel	carpet_lighting_cel
	#define light_level 	carpet_light_level

	extern int lighting_cel;
	extern uint8_t light_level;

	int x;
	int y;

	// ST03.MAP only defines the Stage 4 tile sections in terms of fully-lit
	// carpet tiles. On lower light levels, we therefore need to override any
	// tiles that were newly scrolled in at the end of the last frame.
	//
	// ZUN landmine: However, this function is only called *after* the game
	// rendered the regular tiles for this frame – both if it rendered all of
	// them (on the first frame of the stage) or just the invalidated ones. If
	// the game scrolled in new tiles at the end of the previous frame, their
	// first lines were therefore already rendered to VRAM in their fully-lit
	// form. And thanks to page flipping, any invalidations we do here won't
	// even apply to the same VRAM page, leaving these lines in VRAM until
	// they're hopefully invalidated in the frame after the next one- This can
	// only ever not glitch because newly scrolled-in lines are covered by the
	// opaque black TRAM cells above the playfield during their first two
	// frames on the playfield…
	//
	// ZUN landmine: …and if the height of the invalidation box is at least
	// three times the [scroll_speed], covering the current frame plus the last
	// two. While a hardcoded box height of 2 pixels works for the 0.25-pixel
	// scroll speed that ST03 defines for the length of this animation, the box
	// should really be derived from the [scroll_speed]. To simplify the
	// arithmetic in the necessary calculations, we jump back 4 frames rather
	// than the required three. For the Y position, negating [scroll_speed] and
	// multiplying it by 2 then gets us into the middle of the four sets of
	// lines. For the size, we need to round up the Q12.4 [scroll_speed] to the
	// next integer pixel.
	// The correct box calculation would therefore be:
	//
	// 	tile_invalidate_box.y = ((scroll_speed.to_pixel() + 1) * 4);
	// 	tiles_invalidate_around_xy(to_sp(PLAYFIELD_W / 2), -(scroll_speed * 2));
	//
	// But really, it would have been much simpler to just directly manipulate
	// the tiles inside the loaded .MAP. That would have removed the need for
	// this tile invalidation call and the loop below. The required [tile_ring]
	// manipulation of rendered tiles during the first frame and the animation
	// could have even been replaced with calls to tiles_fill_initial() and
	// tiles_invalidate_all(). Nothing about this would have introduced any
	// drawback, since the entire effect expects that Stage 4's initial tile
	// sections restrict themselves to a single repeating row of tiles anyway.
	tile_invalidate_box.x = PLAYFIELD_W;
	tile_invalidate_box.y = 2;
	tiles_invalidate_around_xy(to_sp(PLAYFIELD_W / 2), 0);

	y = (scroll_line / TILE_H);
	for(x = 0; x < TILES_X; x++) {
		// Override any tiles that have not yet been touched by the animation
		// (= 2) towards the next light level with the respective image on the
		// current light level.
		// ZUN landmine: This should really also override the tiles that *have*
		// been animated (= 0) with the image from the *next* light level.
		// Otherwise, these tiles would wrongly appear fully lit even on light
		// level 1. This only doesn't matter in the original game because
		// 1) the [scroll_speed] is slow enough, and
		// 2) the animation onto the final light level 2 follows directly after
		//    the level 1 animation, making wrong tiles not stick out as much
		//    during the few frames they would be visible.
		if(CARPET_LIGHTING_ANIM[lighting_cel][x] == 2) {
			tile_ring[y][x] = (CARPET_TILE_IMAGE_VOS[light_level][x]);
		}
	}

	if(stage_frame <= 1) {
		for(y = 0; y < TILES_Y; y++) {
			for(x = 0; x < TILES_X; x++) {
				tile_ring[y][x] = CARPET_TILE_IMAGE_VOS[0][x];
			}
		}
		tiles_invalidate_all();
		light_level = 0;
	} else if(light_level == 0) {
		if(stage_frame >= 1664) { // 29.5 seconds into the stage
			carpet_lighting_update_and_render(lighting_cel, light_level, 1);
		}
	} else if(light_level == 1) {
		carpet_lighting_update_and_render(lighting_cel, light_level, 2);
	} else {
		stage_render = nullfunc_near;
	}

	#undef light_level
	#undef lighting_cel
}

/// -------

/// Stage 5
/// -------

#define star_center_y	stage5_star_center_y
#define STAR_COUNT  	STAGE5_STAR_COUNT

static const pixel_t STAR_W = 96;
static const pixel_t STAR_H = 80;
static const pixel_t STAR_VELOCITY_Y = 4;
static const pixel_t STAR_MARGIN = (
	((PLAYFIELD_W - (STAR_W * STAR_COUNT)) / STAR_COUNT) / 2
);

static const pixel_t STAR_MARGIN_W = (STAR_MARGIN + STAR_W + STAR_MARGIN);

void pascal near stage5_render(void)
{
	if(
		(boss.phase >= PHASE_BOSS_ENTRANCE_BB) &&
		(boss.phase < PHASE_EXPLODE_BIG)
	) {
		return;
	}
	for(int i = 0; i < STAR_COUNT; i++) {
		star_center_y[i].v += to_sp(STAR_VELOCITY_Y);
		if(star_center_y[i].v >= to_sp(RES_Y)) {
			star_center_y[i].v -= to_sp(RES_Y);
		}

		vram_y_t top = scroll_subpixel_y_to_vram_seg1(
			star_center_y[i].v + to_sp(PLAYFIELD_TOP - (STAR_H / 2))
		);
		cdg_put_plane_roll_8(
			(PLAYFIELD_LEFT + STAR_MARGIN + (i * STAR_MARGIN_W)),
			top,
			CDG_BG_2,
			PL_B,
			reinterpret_cast<dots8_t __seg *>(SEG_PLANE_E)
		);
	}
}

void pascal near stage5_invalidate(void)
{
	tile_invalidate_box.x = STAR_W;
	tile_invalidate_box.y = STAR_H;
	for(int i = 0; i < STAR_COUNT; i++) {
		tiles_invalidate_around_xy(
			(to_sp(STAR_MARGIN + (STAR_W / 2)) + (i * to_sp(STAR_MARGIN_W))),
			(star_center_y[i].v - to_sp(STAR_VELOCITY_Y))
		);
	}
}

#undef STAR_COUNT
#undef star_center_y
/// -------

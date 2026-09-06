						bullet->spawn_flag = BSF_GRAZED;
						if(stage_graze < STAGE_GRAZE_CAP) {
							stage_graze++;
							hud_graze_put();
							score_delta += graze_score;
						}
					}
				}
			}

			if(is_pellet(i)) {
				pellets_render[pellets_render_count].top.left = (
					bullet->pos.cur.to_screen_left(PELLET_W)
				);
				pellets_render[pellets_render_count].top.top = (
					bullet->pos.cur.to_vram_top_scrolled_seg3(PELLET_H)
				);
				pellets_render_count++;
			}
		}
		if(turbo_mode == false) {
#if (GAME == 5)
			slowdown_caused_by_bullets = false;
			i = 42;
#else
			i = 24;
			i += playperf;
#endif
			i += (rank * 8);
			if(bullets_seen >= i) {
				if(!stage_frame_mod2) {
					slowdown_factor = 2;
#if (GAME == 5)
					slowdown_caused_by_bullets = true;
#endif
				}
			} else if(bullets_seen >= (i + SLOWDOWN_BULLET_THRESHOLD_UNUSED)) {
				// Yes, never executed, as the first condition would then have
				// been true as well
				slowdown_factor = 2;
#if (GAME == 5)
				slowdown_caused_by_bullets = true;
#endif
			}
		}
	} else {
		// A bit wasteful to run all of this every frame, since no new bullets
		// are spawned while [bullet_zap] is active; the bullet spawn wrapper
		// functions prevent that. Then again, this means that the code here
		// does kind of rely on bullets not being spawned through other methods.

		unsigned int score_per_bullet;
		unsigned int score_step;

		// Without this cap, the [popup_bonus] formula would be
		// 	0.5n³ - n² + 1.5n
		// with n = [bullets_seen].
		unsigned int score_per_bullet_cap;
		unsigned char patnum;

		patnum =
			(PAT_BULLET_ZAP + (bullet_zap.frame / BULLET_ZAP_FRAMES_PER_CEL)
		);
		score_per_bullet = 1;
		score_step = 1;
#if (GAME == 5)
		// ZUN quirk: All code below uses TH04's patnum for that sprite.
		// This causes the decay animation to never actually play in TH05.
		#define PAT_BULLET_ZAP 72

		score_per_bullet_cap = (rank == RANK_EXTRA)
			? 1600
			: select_for_rank(960, 1280, 1280, 1280);
#else
		switch(rank) {
		case RANK_EASY:
			score_per_bullet_cap = 1000;
			break;
		case RANK_NORMAL:
		case RANK_HARD:
		case RANK_LUNATIC:
			score_per_bullet_cap = 1600;
			break;
		case RANK_EXTRA:
			score_per_bullet_cap = 2000;
			break;
		}
#endif

		overlay_popup_bonus = 0;
		for(i = 0; i < BULLET_COUNT; i++, bullet--) {
			if(bullet->flag != F_ALIVE) {
				continue;
			}
			bullet->pos.velocity.set(0.0f, 0.0f);
			bullet->pos.update_seg3();

			// ZUN quirk: Always false in TH05, see above
			if(patnum < (PAT_BULLET_ZAP + BULLET_DECAY_CELS)) {
				bullet->patnum = patnum;
#if (GAME == 5)
				bullets_seen++;
#endif
				continue;
			}
			overlay_popup_bonus += score_per_bullet;
			score_delta += score_per_bullet;
			pointnums_add_white(
				bullet->pos.cur.x, bullet->pos.cur.y, score_per_bullet
			);

			score_per_bullet += score_step;
			score_step += 3;
			if(score_per_bullet > score_per_bullet_cap) {
				score_per_bullet = score_per_bullet_cap;
			}

			bullet->flag = F_REMOVE;
#if (GAME == 5)
			if(bullet_zap_drop_point_items && ((bullets_seen % 4) == 0)) {
				items_add(bullet->pos.cur.x, bullet->pos.cur.y, IT_POINT);
			}
			bullets_seen++;
#endif
		}
		// Note that this would show only one popup even *if* bullets could
		// spawn during the zap frames: Popups can be changed at least every
		// 64 frames, and BULLET_ZAP_FRAMES is smaller.
		if(overlay_popup_bonus) {
			overlay_popup_show(POPUP_ID_BONUS);
		}
		bullet_zap.frame++;

		// ZUN quirk: Always true in TH05, see above
		if(patnum >= (PAT_BULLET_ZAP + BULLET_ZAP_CELS)) {
			bullet_zap.active = false;
		}
	}
	if(bullet_clear_time) {
		bullet_clear_time--;
	}
}

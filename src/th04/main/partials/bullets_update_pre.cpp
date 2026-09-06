void bullets_update(void)
{
	int i;
	int bullets_seen = 0;
#if (GAME == 5)
	pellet_clouds_render_count = 0;
#endif
	pellets_render_count = 0;
	bullet_t near *bullet = &bullets[BULLET_COUNT - 1];

	// Since we iterate over the bullet array backwards, we encounter the 16×16
	// bullets first.
	#define is_bullet16(i) \
		(i < BULLET16_COUNT)

	#define is_pellet(i) \
		!is_bullet16(i)

	if(bullet_zap.active == false) {
		for(i = 0; i < BULLET_COUNT; i++, bullet--) {
			if(bullet->flag == F_FREE) {
				continue;
			}
			if(bullet->flag == F_REMOVE) {
				bullet->flag = F_FREE;
				continue;
			}
			bullets_seen++;
			if(bullet_clear_time) {
				if(bullet->move_flag < BMF_DECAY) {
					bullet->move_flag = BMF_DECAY;
					bullet->patnum = is_bullet16(i)
						? PAT_DECAY_BULLET16
						: PAT_DECAY_PELLET;

					if(bullet->age != 0) {
						score_delta += 100;
					} else {
						score_delta += 10;
					}
				} else {
					reinterpret_cast<unsigned char &>(bullet->move_flag)++;
					if(bullet->move_flag >= BMF_DECAY_END) {
						bullet->pos.update_seg3();
						bullet->flag = F_REMOVE;
						continue;
					}
					if((bullet->move_flag % BMF_DECAY_FRAMES_PER_CEL) == 0) {
						bullet->patnum++;
					}
				}
			}
			bullet->age++;
			if(bullet->spawn_flag >= BSF_ACTIVE) {
				if(bullet->spawn_flag == BSF_ACTIVE) {
					bullet->spawn_flag = BSF_GRAZEABLE;
				} else {
					// In delay cloud state
					if(bullet->spawn_flag == BSF_CLOUD_BACKWARDS) {
						bullet->pos.prev = bullet->pos.cur;
						bullet->pos.cur.x.v -= (bullet->pos.velocity.x.v << 3);
						bullet->pos.cur.y.v -= (bullet->pos.velocity.y.v << 3);
						bullet->spawn_flag = BSF_CLOUD_FORWARDS;
					} else if(bullet->spawn_flag == BSF_CLOUD_FORWARDS) {
						bullet->pos.update_seg3();
					} else {
						bullet->pos.prev = bullet->pos.cur;
						bullet->pos.cur.x.v += (bullet->pos.velocity.x.v / 3);
						bullet->pos.cur.y.v += (bullet->pos.velocity.y.v / 3);
					}
					reinterpret_cast<unsigned char &>(bullet->spawn_flag)++;
					if(bullet->spawn_flag >= BSF_CLOUD_END) {
#if (GAME == 5)
						if(!playfield_encloses_yx_lt_ge(
							bullet->pos.cur.x,
							bullet->pos.cur.y,
							BULLET16_W,
							BULLET16_H
						)) {
							bullet->flag = F_REMOVE;
							continue;
						}
#endif
						bullet->spawn_flag = BSF_ACTIVE;
					}
#if (GAME == 5)
					else if(is_pellet(i)) {
						pellet_clouds_render[pellet_clouds_render_count++] =
							bullet;
					}
#endif
					continue;
				}
			}
			if(bullet->move_flag == BMF_SPECIAL) {
				bullet_update_special(*bullet);
			} else if(bullet->move_flag == BMF_DECELERATE) {
				bullet->u1.decelerate_time--;
				bullet->speed_cur.v = (bullet->speed_final.v + ((
					bullet->u1.decelerate_time *
					bullet->u2.decelerate_speed_delta.v
				) / BMF_DECELERATE_FRAMES));
				if(bullet->u1.decelerate_time == 0) {
					bullet->speed_cur = bullet->speed_final;
					bullet->move_flag = BMF_REGULAR;
				}
				bullet_velocity_set_from_angle_and_speed((*bullet));
			}

			/* DX:AX = */ bullet->pos.update_seg3();
			if(!playfield_encloses(_AX, _DX, BULLET16_W, BULLET16_H)) {
				bullet->flag = F_REMOVE;
				continue;
			}

			if(bullet_clear_time != 0) {
				continue;
			}
			_AX -= player_pos.cur.x.v;
			_DX -= player_pos.cur.y.v;
			if(player_invincibility_time == 0) {
				// Yup, a bullet must have been grazed in a previous frame
				// before it can be collided with.
				if(bullet->spawn_flag != BSF_GRAZEABLE) {
					if(overlap_wh_inplace_fast(
						_AX, _DX, BULLET_KILLBOX_W, BULLET_KILLBOX_H
					)) {
						bullet->flag = F_REMOVE;
						player_is_hit = true;
						continue;
					}
				} else {
					// Yes, the graze box is biased to the right, and taller
					// than wide.
					if(overlap_offcenter_inplace_fast(
						_AX, _DX,
						to_sp(16.0f), to_sp(22.0f), to_sp(20.0f), to_sp(22.0f)
					)) {
						/* TODO: Replace with the decompiled call
						 * 	sparks_add_random(bullet->pos.cur.x, bullet->pos.cur.y, to_sp(2.0f), 2);
						 * once that function is part of the same segment */

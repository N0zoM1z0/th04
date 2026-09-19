#pragma option -zCMAIN__TEXT -zPmain_01

#include "src/shared/runtime/api.hpp"
#include "src/main/player/shot.hpp"
#include "compat/rec98/th04/main/homing.hpp"

static const unsigned char REIMU_SHOT_CYCLE_FRAMES = 18;
extern "C" unsigned char reimu_shot_cycle;

static void pascal near reimu_homing_set(Shot near *shot, unsigned char angle)
{
	angle += iatan2(
		(homing_target.y.v - player_pos.cur.y.v),
		(homing_target.x.v - shot->pos.cur.x.v)
	);
	shot_velocity_set(&shot->pos.velocity, angle);
}

extern "C" void near shot_reimu_l0(void)
{
	Shot near *shot;
	shot_ptr = shots;
	shot_last_id = 0;
	if((shot = shots_add()) != 0) {
		shot->patnum_base = 0x1C;
		shot->damage = 10;
	}
}

extern "C" void near shot_reimu_l1(void)
{
	Shot near *shot;
	shot_ptr = shots;
	shot_last_id = 0;
	if((shot = shots_add()) != 0) {
		shot_velocity_set(
			&shot->pos.velocity,
			(static_cast<unsigned char>(randring1_next16_and(7)) - 0x44)
		);
		shot->patnum_base = 0x1C;
		shot->damage = 10;
	}
}

extern "C" void near shot_reimu_a_l2(void)
{
	int shot_count = 1;
	Shot near *shot;
	if(shot_time == REIMU_SHOT_CYCLE_FRAMES) {
		reimu_shot_cycle = 0;
	}
	if((reimu_shot_cycle % 3) == 0) {
		shot_count += 2;
	}
	reimu_shot_cycle++;
	shot_ptr = shots;
	shot_last_id = 0;
	while((shot = shots_add()) != 0) {
		if(shot_count == 1) {
			shot_velocity_set(
				&shot->pos.velocity,
				(static_cast<unsigned char>(randring1_next16_and(0xF)) - 0x48)
			);
			shot->patnum_base = 0x1C;
		} else {
			if(shot_count == 3) {
				shot->pos.cur.x.v -= TO_SP(24);
			} else {
				shot->pos.cur.x.v += TO_SP(24);
			}
			if(homing_target.y.v != Subpixel::None()) {
				reimu_homing_set(
					shot,
					(static_cast<unsigned char>(randring1_next16_and(7) - 4))
				);
			}
			shot->patnum_base = 0x1E;
		}
		shot->damage = 10;
		if(--shot_count <= 0) {
			break;
		}
	}
}

extern "C" void near shot_reimu_a_l3(void)
{
	int shot_count = 2;
	Shot near *shot;
	if(shot_time == REIMU_SHOT_CYCLE_FRAMES) {
		reimu_shot_cycle = 0;
	}
	if((reimu_shot_cycle % 3) == 0) {
		shot_count += 2;
	}
	reimu_shot_cycle++;
	shot_ptr = shots;
	shot_last_id = 0;
	while((shot = shots_add()) != 0) {
		if(shot_count <= 2) {
			if(shot_count == 2) {
				shot->pos.cur.x.v -= TO_SP(8);
			} else {
				shot->pos.cur.x.v += TO_SP(8);
			}
			shot->patnum_base = 0x1C;
			shot->damage = 9;
		} else {
			if(shot_count == 4) {
				shot->pos.cur.x.v -= TO_SP(24);
			} else {
				shot->pos.cur.x.v += TO_SP(24);
			}
			if(homing_target.y.v != Subpixel::None()) {
				reimu_homing_set(
					shot,
					(static_cast<unsigned char>(randring1_next16_and(7) - 4))
				);
			}
			shot->patnum_base = 0x1E;
			shot->damage = 10;
		}
		if(--shot_count <= 0) {
			break;
		}
	}
}

extern "C" void near shot_reimu_a_l4(void)
{
	int shot_count = 3;
	unsigned char angle;
	Shot near *shot;
	if(shot_time == REIMU_SHOT_CYCLE_FRAMES) {
		reimu_shot_cycle = 0;
	}
	if((reimu_shot_cycle % 3) == 0) {
		shot_count += 2;
	}
	reimu_shot_cycle++;
	angle = -0x46;
	shot_ptr = shots;
	shot_last_id = 0;
	while((shot = shots_add()) != 0) {
		if(shot_count <= 3) {
			shot_velocity_set(&shot->pos.velocity, angle);
			shot->patnum_base = 0x1C;
			shot->damage = 8;
			angle += 6;
		} else {
			if(shot_count == 5) {
				shot->pos.cur.x.v -= TO_SP(24);
			} else {
				shot->pos.cur.x.v += TO_SP(24);
			}
			if(homing_target.y.v != Subpixel::None()) {
				reimu_homing_set(
					shot,
					(static_cast<unsigned char>(randring1_next16_and(7) - 4))
				);
			}
			shot->patnum_base = 0x1E;
			shot->damage = 9;
		}
		if(--shot_count <= 0) {
			break;
		}
	}
}

extern "C" void near shot_reimu_a_l5(void)
{
	int shot_count = 3;
	unsigned char angle;
	Shot near *shot;
	if(shot_time == REIMU_SHOT_CYCLE_FRAMES) {
		reimu_shot_cycle = 0;
	}
	if((reimu_shot_cycle % 2) == 0) {
		shot_count += 2;
	}
	reimu_shot_cycle++;
	angle = -0x48;
	shot_ptr = shots;
	shot_last_id = 0;
	while((shot = shots_add()) != 0) {
		if(shot_count <= 3) {
			shot_velocity_set(&shot->pos.velocity, angle);
			shot->patnum_base = 0x1C;
			shot->damage = 8;
			angle += 8;
		} else {
			if(shot_count == 5) {
				shot->pos.cur.x.v -= TO_SP(24);
			} else {
				shot->pos.cur.x.v += TO_SP(24);
			}
			if(homing_target.y.v != Subpixel::None()) {
				reimu_homing_set(
					shot,
					(static_cast<unsigned char>(randring1_next16_and(7) - 4))
				);
			}
			shot->patnum_base = 0x1E;
			shot->damage = 9;
		}
		if(--shot_count <= 0) {
			break;
		}
	}
}

extern "C" void near shot_reimu_a_l6(void)
{
	int shot_count = 3;
	unsigned char angle;
	Shot near *shot;
	if(shot_time == REIMU_SHOT_CYCLE_FRAMES) {
		reimu_shot_cycle = 0;
	}
	if((reimu_shot_cycle % 2) == 0) {
		shot_count += 2;
	}
	reimu_shot_cycle++;
	angle = -0x48;
	shot_ptr = shots;
	shot_last_id = 0;
	while((shot = shots_add()) != 0) {
		if(shot_count <= 3) {
			shot_velocity_set(&shot->pos.velocity, angle);
			shot->patnum_base = 0x1C;
			shot->damage = 7;
			angle += 8;
		} else {
			if(shot_count == 5) {
				shot->pos.cur.x.v -= TO_SP(24);
			} else {
				shot->pos.cur.x.v += TO_SP(24);
			}
			if(homing_target.y.v != Subpixel::None()) {
				reimu_homing_set(
					shot,
					(static_cast<unsigned char>(randring1_next16_and(7) - 4))
				);
			}
			shot->patnum_base = 0x1E;
			shot->damage = 8;
		}
		if(--shot_count <= 0) {
			break;
		}
	}
}

extern "C" void near shot_reimu_a_l7(void)
{
	int shot_count = 5;
	unsigned char angle_1;
	unsigned char angle_2;
	Shot near *shot;
	if(shot_time == REIMU_SHOT_CYCLE_FRAMES) {
		reimu_shot_cycle = 0;
	}
	if((reimu_shot_cycle % 2) == 0) {
		shot_count += 2;
	}
	reimu_shot_cycle++;
	angle_1 = -0x46;
	shot_ptr = shots;
	shot_last_id = 0;
	while((shot = shots_add()) != 0) {
		if(shot_count <= 3) {
			shot_velocity_set(&shot->pos.velocity, angle_1);
			shot->patnum_base = 0x1C;
			shot->damage = 4;
			shot->damage = 7;
			angle_1 += 6;
		} else if(shot_count <= 5) {
			if(shot_count == 5) {
				shot->pos.cur.x.v -= TO_SP(24);
				angle_2 = -0x48;
			} else {
				shot->pos.cur.x.v += TO_SP(24);
				angle_2 = -0x38;
			}
			shot_velocity_set(&shot->pos.velocity, angle_2);
			shot->patnum_base = 0x1C;
			shot->damage = 7;
		} else {
			if(shot_count == 7) {
				shot->pos.cur.x.v -= TO_SP(24);
			} else {
				shot->pos.cur.x.v += TO_SP(24);
			}
			if(homing_target.y.v != Subpixel::None()) {
				reimu_homing_set(
					shot,
					(static_cast<unsigned char>(randring1_next16_and(7) - 4))
				);
			}
			shot->patnum_base = 0x1E;
			shot->damage = 7;
		}
		if(--shot_count <= 0) {
			break;
		}
	}
}

extern "C" void near shot_reimu_a_l8(void)
{
	int shot_count = 5;
	unsigned char angle_1;
	unsigned char angle_2;
	Shot near *shot;
	shot_count += 2;
	reimu_shot_cycle++;
	angle_1 = -0x46;
	shot_ptr = shots;
	shot_last_id = 0;
	while((shot = shots_add()) != 0) {
		if(shot_count <= 3) {
			shot_velocity_set(&shot->pos.velocity, angle_1);
			shot->patnum_base = 0x1C;
			shot->damage = 7;
			angle_1 += 6;
		} else if(shot_count <= 5) {
			if(shot_count == 5) {
				shot->pos.cur.x.v -= TO_SP(24);
				angle_2 = -0x48;
			} else {
				shot->pos.cur.x.v += TO_SP(24);
				angle_2 = -0x38;
			}
			shot_velocity_set(&shot->pos.velocity, angle_2);
			shot->patnum_base = 0x1C;
			shot->damage = 7;
		} else {
			if(shot_count == 7) {
				shot->pos.cur.x.v -= TO_SP(24);
			} else {
				shot->pos.cur.x.v += TO_SP(24);
			}
			if(homing_target.y.v != Subpixel::None()) {
				reimu_homing_set(
					shot,
					(static_cast<unsigned char>(randring1_next16_and(7) - 4))
				);
			}
			shot->patnum_base = 0x1E;
			shot->damage = 7;
		}
		if(--shot_count <= 0) {
			break;
		}
	}
}

extern "C" void near shot_reimu_a_l9(void)
{
	int shot_count = 5;
	unsigned char angle_1;
	unsigned char angle_2;
	Shot near *shot;
	shot_count += 2;
	if(shot_time == REIMU_SHOT_CYCLE_FRAMES) {
		reimu_shot_cycle = 0;
	}
	if((reimu_shot_cycle % 2) == 0) {
		shot_count += 2;
	}
	reimu_shot_cycle++;
	angle_1 = -0x46;
	shot_ptr = shots;
	shot_last_id = 0;
	while((shot = shots_add()) != 0) {
		if(shot_count <= 3) {
			shot_velocity_set(&shot->pos.velocity, angle_1);
			shot->patnum_base = 0x1C;
			shot->damage = 6;
			angle_1 += 6;
		} else if(shot_count <= 5) {
			if(shot_count == 5) {
				shot->pos.cur.x.v -= TO_SP(24);
				angle_2 = -0x48;
			} else {
				shot->pos.cur.x.v += TO_SP(24);
				angle_2 = -0x38;
			}
			shot_velocity_set(&shot->pos.velocity, angle_2);
			shot->patnum_base = 0x1C;
			shot->damage = 7;
		} else if(shot_count <= 7) {
			if(shot_count == 7) {
				shot->pos.cur.x.v -= TO_SP(24);
				angle_2 = -0x4C;
			} else {
				shot->pos.cur.x.v += TO_SP(24);
				angle_2 = -0x34;
			}
			if(homing_target.y.v != Subpixel::None()) {
				reimu_homing_set(
					shot,
					(static_cast<unsigned char>(randring1_next16_and(7) - 4))
				);
			} else {
				shot_velocity_set(&shot->pos.velocity, angle_2);
			}
			shot->patnum_base = 0x1E;
			shot->damage = 5;
		} else {
			if(shot_count == 9) {
				shot->pos.cur.x.v -= TO_SP(24);
			} else {
				shot->pos.cur.x.v += TO_SP(24);
			}
			if(homing_target.y.v != Subpixel::None()) {
				reimu_homing_set(shot, 0);
			}
			shot->patnum_base = 0x1E;
			shot->damage = 7;
		}
		if(--shot_count <= 0) {
			break;
		}
	}
}

extern "C" void near shot_reimu_b_l2(void)
{
	int shot_count = 1;
	unsigned char angle;
	Shot near *shot;
	if(shot_time == REIMU_SHOT_CYCLE_FRAMES) {
		reimu_shot_cycle = 0;
	}
	if((reimu_shot_cycle % 3) == 0) {
		shot_count += 2;
	}
	reimu_shot_cycle++;
	shot_ptr = shots;
	shot_last_id = 0;
	while((shot = shots_add()) != 0) {
		if(shot_count == 1) {
			shot_velocity_set(
				&shot->pos.velocity,
				(static_cast<unsigned char>(randring1_next16_and(0xF)) - 0x48)
			);
			shot->patnum_base = 0x1C;
		} else {
			if(shot_count == 3) {
				shot->pos.cur.x.v -= TO_SP(24);
				angle = -0x48;
			} else {
				shot->pos.cur.x.v += TO_SP(24);
				angle = -0x38;
			}
			shot_velocity_set(&shot->pos.velocity, angle);
			shot->patnum_base = 0x20;
		}
		shot->damage = 10;
		if(--shot_count <= 0) {
			break;
		}
	}
}

extern "C" void near shot_reimu_b_l3(void)
{
	int shot_count = 2;
	subpixel_t x;
	unsigned char angle;
	Shot near *shot;
	if(shot_time == REIMU_SHOT_CYCLE_FRAMES) {
		reimu_shot_cycle = 0;
	}
	if((reimu_shot_cycle % 3) == 0) {
		shot_count += 2;
	}
	reimu_shot_cycle++;
	shot_ptr = shots;
	shot_last_id = 0;
	while((shot = shots_add()) != 0) {
		if(shot_count <= 2) {
			if(shot_count == 2) {
				x = -TO_SP(8);
			} else {
				x = TO_SP(8);
			}
			shot->patnum_base = 0x1C;
		} else {
			if(shot_count == 4) {
				x = -TO_SP(24);
				angle = -0x48;
			} else {
				x = TO_SP(24);
				angle = -0x38;
			}
			shot_velocity_set(&shot->pos.velocity, angle);
			shot->patnum_base = 0x20;
		}
		shot->damage = 9;
		shot->pos.cur.x.v += x;
		if(--shot_count <= 0) {
			break;
		}
	}
}

extern "C" void near shot_reimu_b_l4(void)
{
	int shot_count = 3;
	subpixel_t x;
	unsigned char angle_1;
	unsigned char angle_2;
	Shot near *shot;
	if(shot_time == REIMU_SHOT_CYCLE_FRAMES) {
		reimu_shot_cycle = 0;
	}
	if((reimu_shot_cycle % 2) == 0) {
		shot_count += 2;
	}
	reimu_shot_cycle++;
	angle_1 = -0x46;
	shot_ptr = shots;
	shot_last_id = 0;
	while((shot = shots_add()) != 0) {
		if(shot_count <= 3) {
			x = 0;
			shot_velocity_set(&shot->pos.velocity, angle_1);
			shot->patnum_base = 0x1C;
			shot->damage = 9;
			angle_1 += 6;
		} else {
			if(shot_count == 5) {
				x = -TO_SP(24);
				angle_2 = -0x48;
			} else {
				x = TO_SP(24);
				angle_2 = -0x38;
			}
			shot_velocity_set(&shot->pos.velocity, angle_2);
			shot->patnum_base = 0x20;
			shot->damage = 9;
		}
		shot->pos.cur.x.v += x;
		if(--shot_count <= 0) {
			break;
		}
	}
}

extern "C" void near shot_reimu_b_l5(void)
{
	int shot_count = 3;
	subpixel_t x;
	unsigned char angle_1;
	unsigned char angle_2;
	Shot near *shot;

	if(shot_time == REIMU_SHOT_CYCLE_FRAMES) {
		reimu_shot_cycle = 0;
	}
	if((reimu_shot_cycle % 2) == 0) {
		shot_count += 4;
	}
	reimu_shot_cycle++;
	angle_1 = -0x46;
	shot_ptr = shots;
	shot_last_id = 0;

	while((shot = shots_add()) != 0) {
		if(shot_count <= 3) {
			x = 0;
			shot_velocity_set(&shot->pos.velocity, angle_1);
			shot->patnum_base = 0x1C;
			shot->damage = 8;
			angle_1 += 7;
		} else {
			if(shot_count >= 6) {
				x = -TO_SP(24);
			} else {
				x = TO_SP(24);
			}
			switch(shot_count) {
			case 7: angle_2 = -0x4E; break;
			case 6: angle_2 = -0x47; break;
			case 5: angle_2 = -0x32; break;
			case 4: angle_2 = -0x39; break;
			}
			shot_velocity_set(&shot->pos.velocity, angle_2);
			shot->patnum_base = 0x20;
			shot->damage = 9;
		}
		shot->pos.cur.x.v += x;
		if(--shot_count <= 0) {
			break;
		}
	}
}

extern "C" void near shot_reimu_b_l6(void)
{
	int shot_count = 3;
	subpixel_t x;
	unsigned char angle_1;
	unsigned char angle_2;
	Shot near *shot;

	if(shot_time == REIMU_SHOT_CYCLE_FRAMES) {
		reimu_shot_cycle = 0;
	}
	if((reimu_shot_cycle % 2) == 0) {
		shot_count += 4;
	}
	reimu_shot_cycle++;
	angle_1 = -0x46;
	shot_ptr = shots;
	shot_last_id = 0;

	while((shot = shots_add()) != 0) {
		if(shot_count <= 3) {
			x = 0;
			shot_velocity_set(&shot->pos.velocity, angle_1);
			shot->patnum_base = 0x1C;
			shot->damage = 8;
			angle_1 += 6;
		} else {
			if(shot_count >= 6) {
				x = -TO_SP(24);
			} else {
				x = TO_SP(24);
			}
			switch(shot_count) {
			case 7: angle_2 = -0x4E; break;
			case 6: angle_2 = -0x47; break;
			case 5: angle_2 = -0x32; break;
			case 4: angle_2 = -0x39; break;
			}
			shot_velocity_set(&shot->pos.velocity, angle_2);
			shot->patnum_base = 0x20;
			shot->damage = 9;
		}
		shot->pos.cur.x.v += x;
		if(--shot_count <= 0) {
			break;
		}
	}
}

extern "C" void near shot_reimu_b_l7(void)
{
	int shot_count = 3;
	subpixel_t x;
	unsigned char angle_1;
	unsigned char angle_2;
	Shot near *shot;

	if(shot_time == REIMU_SHOT_CYCLE_FRAMES) {
		reimu_shot_cycle = 0;
	}
	if((reimu_shot_cycle % 2) == 0) {
		shot_count += 4;
	}
	reimu_shot_cycle++;
	angle_1 = -0x46;
	shot_ptr = shots;
	shot_last_id = 0;

	while((shot = shots_add()) != 0) {
		if(shot_count <= 3) {
			x = 0;
			shot_velocity_set(&shot->pos.velocity, angle_1);
			shot->patnum_base = 0x1C;
			shot->damage = 8;
			angle_1 += 6;
		} else {
			if(shot_count >= 6) {
				x = -TO_SP(24);
			} else {
				x = TO_SP(24);
			}
			switch(shot_count) {
			case 7: angle_2 = -0x4E; break;
			case 6: angle_2 = -0x47; break;
			case 5: angle_2 = -0x32; break;
			case 4: angle_2 = -0x39; break;
			}
			shot_velocity_set(&shot->pos.velocity, angle_2);
			shot->patnum_base = 0x20;
			shot->damage = 9;
		}
		shot->pos.cur.x.v += x;
		if(--shot_count <= 0) {
			break;
		}
	}
}

extern "C" void near shot_reimu_b_l8(void)
{
	int shot_count = 5;
	subpixel_t x;
	unsigned char angle_1;
	unsigned char angle_2;
	Shot near *shot;

	if(shot_time == REIMU_SHOT_CYCLE_FRAMES) {
		reimu_shot_cycle = 0;
	}
	if((reimu_shot_cycle % 2) == 0) {
		shot_count += 4;
	}
	reimu_shot_cycle++;
	angle_1 = -0x48;
	shot_ptr = shots;
	shot_last_id = 0;

	while((shot = shots_add()) != 0) {
		if(shot_count <= 5) {
			x = 0;
			shot_velocity_set(&shot->pos.velocity, angle_1);
			shot->patnum_base = 0x1C;
			shot->damage = 8;
			angle_1 += 4;
		} else {
			if(shot_count >= 8) {
				x = -TO_SP(24);
			} else {
				x = TO_SP(24);
			}
			switch(shot_count) {
			case 9: angle_2 = -0x4E; break;
			case 8: angle_2 = -0x47; break;
			case 7: angle_2 = -0x32; break;
			case 6: angle_2 = -0x39; break;
			}
			shot_velocity_set(&shot->pos.velocity, angle_2);
			shot->patnum_base = 0x20;
			shot->damage = 9;
		}
		shot->pos.cur.x.v += x;
		if(--shot_count <= 0) {
			break;
		}
	}
}

extern "C" void near shot_reimu_b_l9(void)
{
	int shot_count = 7;
	subpixel_t x;
	unsigned char angle_1;
	unsigned char angle_2;
	Shot near *shot;

	if(shot_time == REIMU_SHOT_CYCLE_FRAMES) {
		reimu_shot_cycle = 0;
	}
	if((reimu_shot_cycle % 2) == 0) {
		shot_count += 4;
	}
	reimu_shot_cycle++;
	angle_1 = -0x48;
	shot_ptr = shots;
	shot_last_id = 0;

	while((shot = shots_add()) != 0) {
		if(shot_count <= 5) {
			x = 0;
			shot_velocity_set(&shot->pos.velocity, angle_1);
			shot->patnum_base = 0x1C;
			shot->damage = 8;
			angle_1 += 4;
		} else {
			switch(shot_count) {
			case 10:
			case 11: angle_2 = -0x40; break;
			case 9: angle_2 = -0x54; break;
			case 8: angle_2 = -0x2C; break;
			case 7: angle_2 = -0x4A; break;
			case 6: angle_2 = -0x36; break;
			}
			if((shot_count & 1) != 0) {
				x = -TO_SP(24);
			} else {
				x = TO_SP(24);
			}
			shot_velocity_set(&shot->pos.velocity, angle_2);
			shot->patnum_base = 0x20;
			shot->damage = 9;
		}
		shot->pos.cur.x.v += x;
		if(--shot_count <= 0) {
			break;
		}
	}
}

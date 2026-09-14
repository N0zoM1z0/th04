#pragma option -zCMAIN__TEXT -zPmain_01

#include "compat/rec98/th04/main/player/shot.hpp"

static const unsigned char REIMU_SHOT_CYCLE_FRAMES = 18;

extern "C" unsigned char reimu_shot_cycle;

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

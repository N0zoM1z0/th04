#pragma option -zCMAIN_035_TEXT -zPmain_03
#include "compat/rec98/libs/master.lib/master.hpp"
#pragma codeseg MAI_TEXT main_01
extern "C" void pascal near nullfunc_near(void);
void pascal near midboss1_render(void);
void pascal near midboss2_render(void);
void pascal near midboss3_render(void);
void pascal near midboss4_render(void);
void pascal near midbossx_render(void);
void pascal near orange_bg_render(void);
void pascal near orange_fg_render(void);
void pascal near orange_backdrop_colorfill(void);
void pascal near kurumi_bg_render(void);
void pascal near kurumi_fg_render(void);
void pascal near kurumi_backdrop_colorfill(void);
void pascal near elly_bg_render(void);
void pascal near elly_fg_render(void);
void pascal near elly_backdrop_colorfill(void);
void pascal near reimu_marisa_bg_render(void);
void pascal near reimu_fg_render(void);
void pascal near marisa_fg_render(void);
void pascal near reimu_marisa_backdrop_colorfill(void);
void pascal near yuuka5_bg_render(void);
void pascal near yuuka5_fg_render(void);
void pascal near yuuka5_backdrop_colorfill(void);
void pascal near yuuka6_bg_render(void);
void pascal near yuuka6_fg_render(void);
void pascal near mugetsu_gengetsu_bg_render(void);
void pascal near mugetsu_fg_render(void);
void pascal near mugetsu_gengetsu_backdrop_colorfill(void);
void pascal near gengetsu_fg_render(void);
void pascal near stage5_render(void);
void pascal near stage5_invalidate(void);
void pascal near tiles_render_all(void);
#pragma codeseg
#include "decomp.hpp"
#include "compat/rec98/libs/master.lib/pc98_gfx.hpp"
#include "compat/rec98/th01/math/overlap.hpp"
#include "compat/rec98/th02/hardware/frmdelay.h"
#include "compat/rec98/th03/hardware/palette.hpp"
#include "th04/common.h"
#include "th04/snd/snd.h"
#include "th04/sprites/main_cdg.h"
#if (GAME == 4)
#include "th04/sprites/main_pat.h"
#endif
#include "th04/main/bg.hpp"
#include "th04/main/end.hpp"
#include "th04/main/frames.h"
#include "th04/main/homing.hpp"
#include "th04/main/null.hpp"
#include "th04/main/rank.hpp"
#include "th04/main/quit.hpp"
#include "th04/main/score.hpp"
#include "th04/main/slowdown.hpp"
#include "th04/main/stage/stage.hpp"
#include "th04/main/stage/bonus.hpp"
#include "th04/main/tile/tile.hpp"
#include "th04/main/dialog/dialog.hpp"
#include "th04/main/bullet/clearzap.hpp"
#include "th04/main/item/item.hpp"
#include "th04/main/player/bomb.hpp"
#include "th04/main/player/shot.hpp"
#include "th04/main/midboss/midboss.hpp"
#if (GAME == 5)
#include "compat/rec98/th05/resident.hpp"
#include "compat/rec98/th05/main/boss/boss.hpp"
#else
#include "compat/rec98/th03/formats/cdg.h"
#include "th04/resident.hpp"
#include "th04/formats/bb.h"
#include "th04/formats/dialog.hpp"
#include "th04/main/boss/boss.hpp"
#include "th04/main/boss/backdrop.hpp"
#include "th04/main/boss/bosses.hpp"
#include "th04/shiftjis/fns.hpp"
#endif

extern char aSt00_bmt[], aSt00bk_cdg[], aSt00_bb[];
extern char aSt01_bmt[], aSt01bk_cdg[], aSt01_bb[];
extern char aSt02_bmt[], aSt02bk_cdg[], aSt02_bb[];
extern char aSt03_bmt[], aSt03bk_cdg[], aSt03bk2_cdg[], aSt03_bb[];
extern char aSt04bk_cdg[], aSt04_bb[], aSt04_cdg[];
extern char aSt05_bb[];
extern char st06bk_cdg[], st06_bb[];

#pragma samecodeseg explosions_small_reset

void near boss_reset(void)
{
	boss_update = nullfunc_far;
	boss_fg_render = nullfunc_near;
	boss.phase = PHASE_HP_FILL;
	boss.mode = 0;
	boss.phase_state.patterns_seen = 0;
	boss.phase_frame = 0;
	boss.pos.velocity.set(0, 0);
	boss.damage_this_frame = 0;
	explosions_small_reset();
	boss_phase_timed_out = true;
}

void pascal near bb_boss_load(const char far *fn)
{
	file_ropen(fn);
	bb_boss_seg = HMem<bb_tiles8_t>::alloc(BB_SIZE);
	file_read(bb_boss_seg, BB_SIZE);
	file_close();
}

void far bb_boss_free(void)
{
	if(bb_boss_seg) {
		HMem<bb_tiles8_t>::free(bb_boss_seg);
		bb_boss_seg = 0;
	}
}

void pascal near orange_bg_render(void);
void pascal  far orange_update(void);
void pascal near orange_fg_render(void);
void pascal near orange_backdrop_colorfill(void);

void far stage1_setup(void)
{
	midboss_update_func = midboss1_update;
	midboss_render_func = midboss1_render;
	midboss.frames_until = 3100;
	midboss.pos.cur.x.v = (192 << 4);
	midboss.pos.cur.y.v = (368 << 4);
	midboss.pos.prev.x.v = (192 << 4);
	midboss.pos.prev.y.v = (368 << 4);
	midboss.pos.velocity.x.v = 0;
	midboss.pos.velocity.y.v = (1 << 4);
	midboss.hp = 800;
	boss_reset();
	boss.pos.cur.x.v = (192 << 4);
	boss.pos.prev.x.v = (192 << 4);
	boss.pos.cur.y.v = (40 << 4);
	boss.pos.prev.y.v = (40 << 4);
	boss_bg_render_func = orange_bg_render;
	boss_update_func = orange_update;
	boss_fg_render_func = orange_fg_render;
	boss.sprite = 128;
	boss_hitbox_radius.x.v = (24 << 4);
	boss_hitbox_radius.y.v = (16 << 4);
	boss_backdrop_colorfill = orange_backdrop_colorfill;
	super_entry_bfnt(aSt00_bmt);
	cdg_load_single_noalpha(CDG_BG_BOSS, aSt00bk_cdg, 0);
	bb_boss_load(aSt00_bb);
	Palettes[0].c.r = 255;
	Palettes[0].c.g = 255;
	stage_render = nullfunc_near;
	stage_invalidate = nullfunc_near;
}

#include "th04/main/rank.hpp"

void pascal near kurumi_bg_render(void);
void pascal  far kurumi_update(void);
void pascal near kurumi_fg_render(void);
void pascal near kurumi_backdrop_colorfill(void);
void pascal near elly_bg_render(void);
void pascal  far elly_update(void);
void pascal near elly_fg_render(void);
void pascal near elly_backdrop_colorfill(void);

void far stage2_setup(void)
{
	midboss_update_func = midboss2_update;
	midboss_render_func = midboss2_render;
	midboss.frames_until = 2600;
	midboss.pos.cur.x.v = (192 << 4);
	midboss.pos.cur.y.v = (-32 << 4);
	midboss.pos.prev.x.v = (192 << 4);
	midboss.pos.prev.y.v = (-32 << 4);
	midboss.pos.velocity.x.v = 0;
	midboss.pos.velocity.y.v = (1 << 4);
	midboss.hp = 750;
	midboss.sprite = 0;
	boss_reset();
	boss.pos.cur.x.v = (192 << 4);
	boss.pos.prev.x.v = (192 << 4);
	boss.pos.cur.y.v = (81 << 4);
	boss.pos.prev.y.v = (81 << 4);
	boss_bg_render_func = kurumi_bg_render;
	boss_update_func = kurumi_update;
	boss_fg_render_func = kurumi_fg_render;
	boss.sprite = 0;
	boss_hitbox_radius.x.v = (24 << 4);
	boss_hitbox_radius.y.v = (24 << 4);
	boss_backdrop_colorfill = kurumi_backdrop_colorfill;
	super_entry_bfnt(aSt01_bmt);
	cdg_load_single_noalpha(CDG_BG_BOSS, aSt01bk_cdg, 0);
	bb_boss_load(aSt01_bb);
	boss_statebyte[0] = select_for_rank(255, 128, 32, 8);
	stage_render = nullfunc_near;
	stage_invalidate = nullfunc_near;
}

void far stage3_setup(void)
{
	midboss_update_func = midboss3_update;
	midboss_render_func = midboss3_render;
	midboss.frames_until = 1600;
	midboss.pos.cur.x.v = (192 << 4);
	midboss.pos.cur.y.v = (-32 << 4);
	midboss.pos.prev.x.v = (192 << 4);
	midboss.pos.prev.y.v = (-32 << 4);
	midboss.pos.velocity.x.v = 0;
	midboss.pos.velocity.y.v = (4 << 4);
	midboss.hp = 850;
	midboss.sprite = 0;
	boss_reset();
	boss.pos.cur.x.v = (192 << 4);
	boss.pos.prev.x.v = (192 << 4);
	boss.pos.cur.y.v = (64 << 4);
	boss.pos.prev.y.v = (64 << 4);
	boss_bg_render_func = elly_bg_render;
	boss_update_func = elly_update;
	boss_fg_render_func = elly_fg_render;
	boss.sprite = 0x86;
	boss_hitbox_radius.x.v = (24 << 4);
	boss_hitbox_radius.y.v = (24 << 4);
	boss_backdrop_colorfill = elly_backdrop_colorfill;
	super_entry_bfnt(aSt02_bmt);
	cdg_load_single_noalpha(CDG_BG_BOSS, aSt02bk_cdg, 0);
	bb_boss_load(aSt02_bb);
	stage_render = nullfunc_near;
	stage_invalidate = nullfunc_near;
}

#include "th04/playchar.h"
#include "th04/main/stage/stages.hpp"
void pascal near reimu_marisa_bg_render(void);
void pascal far reimu_update(void);
void pascal near reimu_fg_render(void);
void pascal far marisa_update(void);
void pascal near marisa_fg_render(void);
void pascal near reimu_marisa_backdrop_colorfill(void);

void far stage4_setup(void)
{
	midboss_update_func = midboss4_update;
	midboss_render_func = midboss4_render;
	midboss.frames_until = 2800;
	midboss.pos.cur.x.v = (144 << 4);
	midboss.pos.cur.y.v = (-32 << 4);
	midboss.pos.prev.x.v = (144 << 4);
	midboss.pos.prev.y.v = (-32 << 4);
	midboss.pos.velocity.x.v = (4 << 4);
	midboss.pos.velocity.y.v = (2 << 4);
	midboss.hp = 1200;
	midboss.sprite = 0;
	boss_reset();
	boss.pos.cur.x.v = (192 << 4);
	boss.pos.prev.x.v = (192 << 4);
	boss.pos.cur.y.v = (64 << 4);
	boss.pos.prev.y.v = (64 << 4);
	boss_bg_render_func = reimu_marisa_bg_render;
	if(playchar == PLAYCHAR_MARISA) {
		boss_update_func = reimu_update;
		boss_fg_render_func = reimu_fg_render;
		boss_statebyte[0] = select_for_rank(4, 6, 8, 12);
		boss_statebyte[1] = select_for_rank(16, 12, 8, 6);
		boss_statebyte[2] = select_for_rank(1, 2, 3, 4);
		boss_statebyte[3] = select_for_rank(23, 23, 24, 24);
		boss_statebyte[4] = select_for_rank(8, 9, 9, 10);
		boss_statebyte[5] = select_for_rank(18, 16, 14, 10);
		boss_statebyte[6] = select_for_rank(6, 8, 9, 10);
	} else {
		boss_update_func = marisa_update;
		boss_fg_render_func = marisa_fg_render;
		boss.hp = 6000;
	}
	boss.sprite = 128;
	boss_hitbox_radius.x.v = (24 << 4);
	boss_hitbox_radius.y.v = (24 << 4);
	boss_backdrop_colorfill = reimu_marisa_backdrop_colorfill;
	super_entry_bfnt(aSt03_bmt);
	if(playchar != PLAYCHAR_REIMU) {
		cdg_load_single_noalpha(CDG_BG_BOSS, aSt03bk_cdg, 0);
	} else {
		cdg_load_single_noalpha(CDG_BG_BOSS, aSt03bk2_cdg, 0);
	}
	bb_boss_load(aSt03_bb);
	stage_render = nullfunc_near;
	stage_invalidate = nullfunc_near;
}

void pascal near yuuka5_bg_render(void);
void pascal  far yuuka5_update(void);
void pascal near yuuka5_fg_render(void);
void pascal near yuuka5_backdrop_colorfill(void);

void far stage5_setup(void)
{
	midboss_update_func = nullfunc_far;
	midboss_render_func = nullfunc_near;
	midboss.frames_until = 60000;
	boss_reset();
	boss.pos.cur.x.v = (192 << 4);
	boss.pos.prev.x.v = (192 << 4);
	boss.pos.cur.y.v = (64 << 4);
	boss.pos.prev.y.v = (64 << 4);
	boss_bg_render_func = yuuka5_bg_render;
	boss_update_func = yuuka5_update;
	boss_fg_render_func = yuuka5_fg_render;
	boss.sprite = 128;
	boss_hitbox_radius.x.v = (26 << 4);
	boss_hitbox_radius.y.v = (26 << 4);
	boss_backdrop_colorfill = yuuka5_backdrop_colorfill;
	cdg_load_single_noalpha(CDG_BG_BOSS, aSt04bk_cdg, 0);
	bb_boss_load(aSt04_bb);
	cdg_load_single_noalpha(CDG_BG_2, aSt04_cdg, 0);
	stage5_star_center_y[0].v = (320 << 4);
	stage5_star_center_y[1].v = (40 << 4);
	stage5_star_center_y[2].v = (190 << 4);
	stage_render = stage5_render;
	stage_invalidate = stage5_invalidate;
	boss_statebyte[0] = select_for_rank(144, 160, 168, 180);
}

void pascal near yuuka6_bg_render(void);
void far yuuka6_update(void);
void pascal near yuuka6_fg_render(void);

void far stage6_setup(void)
{
	midboss_update_func = nullfunc_far;
	midboss_render_func = nullfunc_near;
	midboss.frames_until = 60000;
	boss_reset();
	boss.pos.cur.x.v = (192 << 4);
	boss.pos.prev.x.v = (192 << 4);
	boss.pos.cur.y.v = (80 << 4);
	boss.pos.prev.y.v = (80 << 4);
	boss_bg_render_func = yuuka6_bg_render;
	boss_update_func = reinterpret_cast<func_t_near>(yuuka6_update);
	boss_fg_render_func = yuuka6_fg_render;
	boss.sprite = 128;
	boss_hitbox_radius.x.v = (24 << 4);
	boss_hitbox_radius.y.v = (48 << 4);
	bb_boss_load(aSt05_bb);
	stage_render = nullfunc_near;
	stage_invalidate = nullfunc_near;
	boss_statebyte[0] = select_for_rank(48, 64, 80, 96);
	boss_statebyte[1] = select_for_rank(1, 1, 2, 4);
}

void pascal near mugetsu_gengetsu_bg_render(void);
void pascal  far mugetsu_update(void);
void pascal near mugetsu_fg_render(void);
void pascal near mugetsu_gengetsu_backdrop_colorfill(void);

void far stagex_setup(void)
{
	midboss_update_func = midbossx_update;
	midboss_render_func = midbossx_render;
	midboss.frames_until = 5400;
	midboss.pos.cur.x.v = (-16 << 4);
	midboss.pos.cur.y.v = (256 << 4);
	midboss.pos.prev.x.v = (-16 << 4);
	midboss.pos.prev.y.v = (256 << 4);
	midboss.pos.velocity.x.v = (4 << 4);
	midboss.pos.velocity.y.v = (-4 << 4);
	midboss.hp = 4096;
	midboss.sprite = 0;
	midboss.angle = 96;
	boss_reset();
	boss.pos.cur.x.v = (192 << 4);
	boss.pos.prev.x.v = (192 << 4);
	boss.pos.cur.y.v = (80 << 4);
	boss.pos.prev.y.v = (80 << 4);
	boss_bg_render_func = mugetsu_gengetsu_bg_render;
	boss_update_func = mugetsu_update;
	boss_fg_render_func = mugetsu_fg_render;
	boss.sprite = 128;
	boss_hitbox_radius.x.v = (24 << 4);
	boss_hitbox_radius.y.v = (48 << 4);
	boss_backdrop_colorfill = mugetsu_gengetsu_backdrop_colorfill;
	boss_statebyte[0] = 0;
	cdg_load_single_noalpha(CDG_BG_BOSS, st06bk_cdg, 0);
	bb_boss_load(st06_bb);
	stage_render = nullfunc_near;
	stage_invalidate = nullfunc_near;
}

#if (GAME == 5)
// Processes any collision between the player and boss sprites.
void near boss_hittest_player(void);
#else
// Moving on top of the boss doesn't kill the player in TH04.
inline void boss_hittest_player(void) {
}
#endif

int pascal near boss_hittest_shots_damage(
	subpixel_t radius_x, subpixel_t radius_y, int se_on_hit
)
{
	shots_hittest_against_boss = true;
	int ret = shots_hittest(boss.pos.cur, radius_x, radius_y);
	if(ret) {
		snd_se_play(se_on_hit);
	}
	shots_hittest_against_boss = false;
	boss_hittest_player();
	return ret;
}

// Probably only here because the code is largely identical to the boss
// version.
int pascal near midboss_hittest_shots_damage(
	subpixel_t radius_x, subpixel_t radius_y, int se_on_hit
)
{
#if (GAME == 5)
	shots_hittest_against_boss = true;
#endif
	// MODDERS: Just call the inline function.
	shot_hitbox_radius.x.v = radius_x;
	shot_hitbox_radius.y.v = radius_y;
	shot_hitbox_center.x.v = midboss.pos.cur.x.v;
	shot_hitbox_center.y.v = midboss.pos.cur.y.v;
	int ret = shots_hittest();
	if(ret) {
		snd_se_play(se_on_hit);
	}
#if (GAME == 5)
	shots_hittest_against_boss = false;
#endif
	return ret;
}

bool near boss_hittest_shots(void)
{
#if (GAME == 4)
	boss.phase_frame++;
#endif
	boss.damage_this_frame = boss_hittest_shots_damage(
		boss_hitbox_radius.x, boss_hitbox_radius.y, 4
	);
	boss.hp -= boss.damage_this_frame;
	if(boss.hp <= boss.phase_end_hp) {
		return true;
	}
	return false;
}

void near boss_hittest_shots_invincible(void)
{
#if (GAME == 4)
	boss.phase_frame++;
#endif
	boss_hittest_shots_damage(boss_hitbox_radius.x, boss_hitbox_radius.y, 10);
}

void near boss_items_drop(void)
{
	enum {
		DROP_COUNT = 5,
		DROP_AREA_W = TO_SP(BOSS_W * 2),
		DROP_AREA_H = TO_SP(BOSS_H * 2),
	};
	enum drop_set_t {
		DS_POWER,
#if (GAME == 4)
		DS_SMALLPOWER,
#endif
		DS_POINT,
		DS_COUNT,

		_drop_set_t_FORCE_INT16 = 0x7FFF
	};

#if (GAME == 5)
	static const item_type_t BOSS_ITEM_DROPS[DS_COUNT][DROP_COUNT] = {
		// DS_POWER
		{ IT_POWER, IT_POWER, IT_BIGPOWER, IT_POWER, IT_POWER },
#if (GAME == 4)
		 // DS_SMALLPOWER
		{ IT_POWER, IT_POWER, IT_POWER,    IT_POWER, IT_POWER },
#endif
		// DS_POINT
		{ IT_POINT, IT_POINT,    IT_POINT, IT_POINT, IT_POINT },
	};
#else
	extern item_type_t BOSS_ITEM_DROPS[DS_COUNT][DROP_COUNT];
#endif

	int i;
	drop_set_t set;
#if (GAME == 5)
	if(power < POWER_MAX) {
		set = DS_POWER;
	} else {
		set = DS_POINT;
	}
#elif (GAME == 4)
	if(power <= (POWER_MAX - 5)) {
		set = DS_POWER;
	} else if(power < POWER_MAX) {
		set = DS_SMALLPOWER;
	} else {
		set = DS_POINT;
	}
#endif
	subpixel_t left = (boss.pos.cur.x - (DROP_AREA_W / 2));
	subpixel_t top  = (boss.pos.cur.y - (DROP_AREA_H / 2));

	for(i = 0; i < DROP_COUNT; i++) {
		items_add(
			(left + randring2_next16_mod(DROP_AREA_W)),
			(top  + randring2_next16_mod(DROP_AREA_H)),
			BOSS_ITEM_DROPS[set][i]
		);
	}
}

void pascal near boss_phase_next(
	explosion_type_t explosion_type, int next_end_hp
)
{
	if(explosion_type != ET_NONE) {
		boss_explode_small(explosion_type);
		if(!boss_phase_timed_out) {
			bullets_clear();
			boss_items_drop();
		}
	}
	boss_phase_timed_out = true;
	boss.phase++;
	boss.phase_frame = 0;
	boss.mode = 0;
	boss.phase_state.patterns_seen = 0;
	boss.hp = boss.phase_end_hp;
	boss.phase_end_hp = next_end_hp;
}

#if (GAME == 5)
void pascal near boss_defeat_update(unsigned int bonus_units)
#else
// Temporarily declaring these here for alignment reasons.
char st06bk_cdg[] = BOSS_BG_MUGETSU_FN;
char st06_bb[] = BOSS_BB_MUGETSU_FN;

void near boss_defeat_update(void)
#endif
{
#if (GAME == 5)
	if(boss.phase == PHASE_BOSS_EXPLODE_SMALL) {
		if(boss.phase_frame == BDF_SMALL_1) {
			boss.damage_this_frame = 0;
			boss_explode_small(ET_CIRCLE);
			snd_se_play(13);
		}
		if(boss.phase_frame == BDF_SMALL_2) {
			boss_explode_small(ET_VERTICAL);
		}
		if(boss.phase_frame == BDF_BIG) {
			boss_defeat_explode_big(ET_CIRCLE, bonus_units);
			player_invincibility_time = BOSS_DEFEAT_INVINCIBILITY_FRAMES;
		}
		homing_target.x.v = Subpixel::None();
		homing_target.y.v = Subpixel::None();
		return;
	} else if(boss.phase == PHASE_BOSS_EXPLODE_BIG) {
#else
	if(boss.phase == PHASE_EXPLODE_BIG) {
#endif
		if(boss.phase_frame < 12) {
			playfield_shake_x = (stage_frame_mod2 == 0) ? -4 : +4;
			playfield_shake_y = (stage_frame_mod4 <= 1) ? -4 : +4;
		}
		bg_render_bombing_func = tiles_render_all;
		slowdown_factor = 2;
#if (GAME == 4)
		boss.phase_frame++;
#endif
		if((boss.phase_frame % 8) == 0) {
			boss.sprite++;
			if(boss.sprite >= (PAT_ENEMY_KILL_last + 1)) {
				boss.phase++; // = PHASE_NONE
				boss.phase_frame = 0;
				bombing_disabled = true;
#if (GAME == 5)
				boss_fg_render = nullfunc_near;
#endif
			}
		}
		return;
	} // else if(boss.phase == PHASE_NONE) {
	palette_settone_deferred(60);
	if(boss.phase_frame == BDF_DIALOG) {
		resident->graze += stage_graze;
		if(stage_id != (MAIN_STAGE_COUNT - 1)) {
#if (GAME == 5)
			dialog_animate();
			if(stage_id != STAGE_EXTRA) {
				stage_clear_bonus();
			} else {
				stage_allclear_bonus();
				optimization_barrier();
			}
#elif (GAME == 4)
			if((stage_id == 4) && (
				(score.continues_used != 0) || (rank == RANK_EASY)
			)) {
				dialog_load_yuuka5_defeat_bad();
				dialog_animate();
				end_game_bad();
			}
			if(stage_id == STAGE_EXTRA) {
				#define gengetsu_started static_cast<bool>( \
					boss_statebyte[0] \
				)

				// Lol, *now* ZUN hardcoded what's effectively a call to the
				// dialog script 'c' command?
				// ZUN bloat: Should have been part of dialog_animate() all
				// along.
				super_clean(PAT_STAGE, (PAT_STAGE_last + 1));

				dialog_animate();

				if(!gengetsu_started) {
					gengetsu_started = true;
					boss_reset();
					boss.pos.init(
						(PLAYFIELD_W / 2), (playfield_fraction_y(6 / 23.0f))
					);
					bg_render_not_bombing = mugetsu_gengetsu_bg_render;
					boss_update = gengetsu_update;
					boss_fg_render = gengetsu_fg_render;
					boss.sprite = PAT_GENGETSU_TIPPING;
					boss_hitbox_radius.set((GENGETSU_W / 4), (GENGETSU_H / 2));
					bgm_title_id = 15;
					overlay1 = overlay_boss_bgm_update_and_render;
					cdg_free(CDG_BG_BOSS);

					/* TODO: Replace with the decompiled call
					* 	bb_boss_free();
					* once that function is part of this translation unit */
					bb_boss_free();

					cdg_load_single_noalpha(
						CDG_BG_BOSS, BOSS_BG_GENGETSU_FN, 0
					);
					bb_boss_load(BOSS_BB_GENGETSU_FN);
					bombing_disabled = false;
				} else {
					stage_allclear_bonus();
					boss.phase_frame++;
				}
				return;

				#undef gengetsu_started
			}
			dialog_animate();
			stage_clear_bonus();
#endif
		} else {
			stage_allclear_bonus();
		}
	} else if(boss.phase_frame == BDF_FADEOUT) {
#if (GAME == 5)
		// ZUN quirk: TH04 doesn't do this. It's not a problem in stages 1 to 5
		// because the remaining score delta will carry over into the next
		// stage and be added to the score there. During the final and Extra
		// Stage though, the lack of this call causes the Clear Bonus to
		// effectively be capped to
		//
		// 	((BDF_FADEOUT - BDF_DIALOG) * SCORE_DELTA_FRAME_LIMIT)
		//
		// points, as we immediately launch into MAINE.EXE while ignoring the
		// rest of the delta.
		score_delta_commit();

		if(stage_id < STAGE_EXTRA) {
			for(int i = 0; i < SCORE_DIGITS; i++) {
				resident->stage_score[stage_id].digits[i] = score.digits[i];
			}
		}
#endif
		if(stage_id == (MAIN_STAGE_COUNT - 1)) {
			end_game();
		} else if(stage_id == STAGE_EXTRA) {
			end_extra();
		}
		overlay_stage_leave();
		snd_kaja_func(KAJA_SONG_FADE, 10);
	} else if(boss.phase_frame == BDF_NEXT_STAGE) {
		resident->stage++;
#if (GAME == 4)
		resident->stage_ascii++;
#endif
		quit = Q_NEXT_STAGE;
		frame_delay(1);
	}
#if (GAME == 4)
	boss.phase_frame++;
#endif
	homing_target.x.v = Subpixel::None();
	homing_target.y.v = Subpixel::None();
}

#if (GAME == 5)
void near boss_hittest_player(void)
{
	#define delta_x	static_cast<subpixel_t>(_AX)
	#define delta_y	static_cast<subpixel_t>(_DX)

	delta_x = boss.pos.cur.x.v;
	delta_y = boss.pos.cur.y.v;
	delta_x -= player_pos.cur.x.v;
	delta_y -= player_pos.cur.y.v;

	// You probably wouldn't swap X and Y in sane code.
	if(overlap_wh_inplace_fast(
		delta_y, delta_x, to_sp(BOSS_H / 2), to_sp(BOSS_W / 2)
	)) {
		player_is_hit = true;
	}

	#undef delta_y
	#undef delta_x
}
#endif

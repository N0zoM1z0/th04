#pragma option -zCMAIN_035_TEXT -zPmain_03

#include "src/shared/runtime/api.hpp"
#include "th04/main/player/player.hpp"
#include "th04/main/item/item.hpp"
#include "th04/main/item/splash.hpp"
#include "th04/main/pointnum/pointnum.hpp"
#include "th04/main/hud/overlay.hpp"
#include "th04/main/bullet/clearzap.hpp"
#include "th04/main/score.hpp"
#include "src/shared/config/resident.hpp"
#include "th04/math/vector.hpp"
#include "th04/snd/snd.h"
#include "src/main/item/power_overflow.hpp"
#include "src/main/math/randring.hpp"

#pragma codeseg MAIN_035_TEXT main_03
#pragma option -a

extern unsigned char item_drop_cycle;
extern unsigned int max_valued_point_items;
extern unsigned char dream_items_collected;
extern unsigned int dream_score;
extern const unsigned int DREAM_SCORE_PER_ITEMS[8];
extern const unsigned char ENEMY_DROPS[64];
extern unsigned char miss_time;
extern "C" void pascal far playperf_raise(char delta);
extern "C" void pascal far playperf_lower(char delta);
extern "C" unsigned char pascal far IRand(void);
extern "C" void pascal far hud_point_items_put(void);
extern "C" void pascal far hud_dream_put(void);
extern "C" void pascal far sub_11DE6(void);
#define shot_level_update sub_11DE6
void far hud_bombs_put(void);
void far hud_lives_put(void);

void far items_init(void)
{
    // stage_runtime_init() has just filled the 256-byte random ring. This
    // direct IRand() call consumes the following process-LCG value and keeps
    // the enemy-drop sequence from starting at the same table position on
    // every stage.
    item_drop_cycle = (IRand() & 0x0F);
    item_splashes_init();
    items_pull_to_player = false;
    dream_score = 0;
}

void pascal near items_add(subpixel_t x, subpixel_t y, item_type_t type)
{
    register item_t near *item;
    register int i;

    if(type == IT_ENEMY_DROP_NEXT) {
        // Scripted enemies can request the next automatic drop instead of a
        // concrete item. Only every second request creates an item. The byte
        // counter and modulo make the 64-entry table repeat after 128 requests.
        item_drop_cycle++;
        if((item_drop_cycle % 2) != 0) {
            return;
        }
        type = static_cast<item_type_t>(ENEMY_DROPS[(item_drop_cycle / 2) % 64]);
    }

    item = items;
    i = 0;
    for(; i < ITEM_COUNT; (i++, item++)) {
        if(item->flag != F_FREE) {
            continue;
        }
        item->flag = F_ALIVE;
        item->unknown = 0;
        item->pos.cur.x.v = x;
        item->pos.cur.y.v = y;
        item->pos.velocity.x.v = 0;
        item->pos.velocity.y.v = -TO_SP(3);
        item->type = type;
        item->patnum = ITEM_PATNUM[static_cast<unsigned char>(type)];
        item_splashes_add(reinterpret_cast<Subpixel &>(x), reinterpret_cast<Subpixel &>(y));
        item->pulled_to_player = false;
        items_spawned++;
        return;
    }
}

extern "C" void pascal far items_miss_add(void)
{
    int pool_index;
    int miss_velocity_field;
    int big_power_slot;
    int type;
    int discarded_distinct_slot;
    register item_t near *item;
    register int spawned_count;

    big_power_slot = randring2_next16_mod(ITEM_MISS_COUNT);
    // The target consumes a second, distinct slot selection but never uses
    // the result. Its ring advance is observable by every later random-ring
    // caller, so this draw is part of the gameplay sequence.
    do {
        discarded_distinct_slot = randring2_next16_mod(ITEM_MISS_COUNT);
    } while(discarded_distinct_slot == big_power_slot);

    if(player_pos.cur.x.v < TO_SP(PLAYFIELD_W / 3)) {
        miss_velocity_field = MISS_FIELD_LEFT;
    } else if(player_pos.cur.x.v <= TO_SP((PLAYFIELD_W / 3) * 2)) {
        miss_velocity_field = MISS_FIELD_CENTER;
    } else {
        miss_velocity_field = MISS_FIELD_RIGHT;
    }

    // Fill up to five free pool entries. A full pool truncates the drop; no
    // live item is displaced. Non-big slots each consume another shared-ring
    // sample, even when the last-life override below changes them to full
    // power items.
    spawned_count = 0;
    item = items;
    pool_index = 0;
    while(pool_index < ITEM_COUNT) {
        if(item->flag == F_FREE) {
            item->flag = F_ALIVE;
            item->unknown = 0;
            item->pos.cur.x.v = player_pos.cur.x.v;
            item->pos.cur.y.v = player_pos.cur.y.v;
            item->pos.velocity.y = ITEM_MISS_VELOCITIES[miss_velocity_field][0][spawned_count];
            item->pos.velocity.x = ITEM_MISS_VELOCITIES[miss_velocity_field][1][spawned_count];
            item->pulled_to_player = false;
            if(big_power_slot != spawned_count) {
                type = randring2_next16_and(IT_POINT);
            } else {
                type = IT_BIGPOWER;
            }
            if(resident->rem_lives == 1) {
                type = IT_FULLPOWER;
            }
            item->type = static_cast<unsigned char>(type);
            item->patnum = ITEM_PATNUM[type];
            spawned_count++;
            items_spawned++;
            if(spawned_count >= ITEM_MISS_COUNT) {
                return;
            }
        }
        pool_index++;
        item++;
    }
}

static void pascal near item_collect(item_t near *item)
{
    register item_t near *collected_item = item;
    bool use_yellow_point_number;
    register unsigned int base_points;

    use_yellow_point_number = false;

    switch(collected_item->type) {
    case IT_POWER:
        if(power < POWER_MAX) {
            if(power == (POWER_MAX - 1)) {
                overlay_popup_show(POPUP_ID_FULL_POWERUP);
                bullets_clear();
            }
            power++;
            shot_level_update();
            base_points = 1;
            break;
        }
        // At full power, ordinary power items advance a saturating bonus
        // index. Index 42 is the inclusive cap and selects the final entry.
        power_overflow++;
        if(static_cast<unsigned int>(power_overflow) >= POWER_OVERFLOW_MAX) {
            power_overflow = POWER_OVERFLOW_MAX;
            use_yellow_point_number = true;
        }
        base_points = POWER_OVERFLOW_BONUS[power_overflow];
        if(pointnum_times_2) {
            item_playperf_raise++;
        }
        break;

    case IT_POINT:
        // Point items collected in the top 52 pixels receive the fixed
        // maximum. Below that line, the original formula uses subpixel Y.
        if(collected_item->pos.cur.y.v <= TO_SP(52)) {
            base_points = 5120;
            item_playperf_raise += 4;
            max_valued_point_items++;
            use_yellow_point_number = true;
            if(pointnum_times_2) {
                item_playperf_raise += 4;
            }
        } else {
            base_points = (3300 - (collected_item->pos.cur.y.v / 2));
            item_playperf_raise += 2;
            if(pointnum_times_2) {
                item_playperf_raise += 2;
            }
        }
        total_point_items_collected++;
        base_points += dream_score;
        stage_point_items_collected++;
        hud_point_items_put();
        break;

    case IT_DREAM:
        // Seven collected dream items select table entry 7. Later dream items
        // keep that maximum rather than advancing beyond the eight entries.
        if(dream_items_collected <= 6) {
            dream_items_collected++;
        }
        dream_score = DREAM_SCORE_PER_ITEMS[dream_items_collected];
        base_points = dream_score;
        hud_dream_put();
        item_playperf_raise += 2;
        if(pointnum_times_2) {
            item_playperf_raise += 2;
        }
        break;

    case IT_BIGPOWER:
        if(power < POWER_MAX) {
            power += 10;
            if(power >= POWER_MAX) {
                power = POWER_MAX;
                overlay_popup_show(POPUP_ID_FULL_POWERUP);
                bullets_clear();
            }
            shot_level_update();
            base_points = 1;
            break;
        }
        power_overflow += 5;
        // Preserve the target's statement order: it reads the table before
        // clamping. An above-cap read is immediately superseded by the fixed
        // 2560-point reward below. A portable implementation must model the
        // same result without performing an out-of-bounds C++ access.
        base_points = POWER_OVERFLOW_BONUS[power_overflow];
        if(static_cast<unsigned int>(power_overflow) > POWER_OVERFLOW_MAX) {
            power_overflow = POWER_OVERFLOW_MAX;
        }
        if(power_overflow == POWER_OVERFLOW_MAX) {
            base_points = 2560;
            use_yellow_point_number = true;
        }
        break;

    case IT_BOMB:
        resident->rem_bombs++;
        base_points = 100;
        hud_bombs_put();
        break;

    case IT_1UP:
        playperf_raise(3);
        resident->rem_lives++;
        hud_lives_put();
        snd_se_play(7);
        overlay_popup_show(POPUP_ID_EXTEND);
        base_points = 100;
        break;

    case IT_FULLPOWER:
        bullets_clear();
        overlay_popup_show(POPUP_ID_FULL_POWERUP);
        power = POWER_MAX;
        shot_level_update();
        base_points = 100;
        break;
    }

    // pointnum_times_2 is latched while a bomb pulls items toward the player.
    // The score delta is doubled here; pointnums_add_* stores the same latch
    // so the popup renderer can show the multiplier beside base_points.
    if(pointnum_times_2 == false) {
        _EAX = base_points;
    } else {
        _AX = base_points;
        _AX += _AX;
        _EAX = _AX;
    }
    score_delta += _EAX;
    if(use_yellow_point_number == false) {
        pointnums_add_white(
            collected_item->pos.cur.x.v,
            collected_item->pos.cur.y.v,
            base_points
        );
    } else {
        pointnums_add_yellow(
            collected_item->pos.cur.x.v,
            collected_item->pos.cur.y.v,
            base_points
        );
    }
    // Item performance is a byte accumulator. Collection can raise playperf
    // at most once here; any remainder carries into later collections.
    if(item_playperf_raise >= 32) {
        item_playperf_raise -= 32;
        playperf_raise(1);
    }
    items_collected++;
}

static void pascal near item_lower_playperf(item_t near *item)
{
    register item_t near *missed_item = item;

    switch(missed_item->type) {
    case IT_POWER:
    case IT_BIGPOWER:
        item_playperf_lower++;
        break;
    case IT_POINT:
        item_playperf_lower += 2;
        break;
    case IT_DREAM:
        item_playperf_lower += 4;
        break;
    case IT_BOMB:
        playperf_lower(2);
        break;
    case IT_1UP:
        playperf_lower(4);
        break;
    }
    // Crossing 64 spends only 48 units. The resulting carry is historical
    // behavior and makes subsequent item misses reach the threshold sooner.
    if(item_playperf_lower >= 64) {
        item_playperf_lower -= 48;
        playperf_lower(1);
    }
}

void far items_update(void)
{
    unsigned char pull_angle;
    register item_t near *item;
    register int i;

    item = items;
    if(items_pull_to_player) {
        pointnum_times_2 = true;
    } else {
        pointnum_times_2 = false;
    }

    i = 0;
    for(; i < ITEM_COUNT; (i++, item++)) {
        if(item->flag == F_FREE) {
            continue;
        }
        if(item->flag == F_REMOVE) {
            // Removal is deferred for one update so the invalidation pass can
            // erase the sprite at its previous position first.
            item->flag = F_FREE;
            continue;
        }
        if(items_pull_to_player) {
            pointnum_times_2 = true;
            item->pulled_to_player = true;
            pull_angle = iatan2(
                (player_pos.cur.y.v - item->pos.cur.y.v),
                (player_pos.cur.x.v - item->pos.cur.x.v)
            );
            vector2_near(item->pos.velocity, pull_angle, TO_SP(ITEM_PULL_SPEED));
        } else if(item->pulled_to_player) {
            // Ending a bomb cancels the pull immediately rather than letting
            // the last attraction velocity carry into normal item motion.
            item->pos.velocity.x.v = 0;
            item->pos.velocity.y.v = 0;
            item->pulled_to_player = false;
        }

        /* DX:AX = */ item->pos.update_seg3();
        if(
            (static_cast<subpixel_t>(_AX) <= -TO_SP(ITEM_W / 2)) ||
            (static_cast<subpixel_t>(_AX) >= TO_SP(PLAYFIELD_W + (ITEM_W / 2))) ||
            (static_cast<subpixel_t>(_DX) >= TO_SP(PLAYFIELD_H + (ITEM_H / 2)))
        ) {
            item->flag = F_REMOVE;
            item_lower_playperf(item);
            continue;
        }
        if(static_cast<subpixel_t>(_DX) < -TO_SP(ITEM_H / 2)) {
            item->pos.cur.y.v = -TO_SP(ITEM_H / 2);
        }
        if(item->pos.velocity.y.v >= 0) {
            // Once an item reaches the falling half of its arc, horizontal
            // motion stops and only the per-frame gravity below remains.
            item->pos.velocity.x.v = 0;
        }

        if(miss_time == 0) {
            // Unsigned 16-bit subtraction implements an axis-aligned pickup
            // box without an absolute-value helper: values outside either
            // side wrap or exceed the accepted width and fail the comparison.
            _BX = player_pos.cur.x.v;
            _BX += TO_SP(24);
            // The same collision block in the attested TH05 target uses the
            // operand direction selected by TC4J's inline assembler here.
            asm { sub bx, ax; }
            if(_BX > TO_SP(48)) {
                goto no_collect;
            }
            _BX = player_pos.cur.y.v;
            _BX += TO_SP(24);
            asm { sub bx, dx; }
            if(_BX > TO_SP(38)) {
                goto no_collect;
            }
            item_collect(item);
            snd_se_play(11);
            item->flag = F_REMOVE;
            continue;
        }
no_collect:
        item->pos.velocity.y.v++;
    }
    item_splashes_update();
    pointnum_times_2 = false;
}

#pragma codeseg

#pragma option -zCMAIN_035_TEXT -zPmain_03

#include "compat/rec98/libs/master.lib/master.hpp"
#include "th04/main/player/player.hpp"
#include "th04/main/item/item.hpp"
#include "th04/main/item/splash.hpp"
#include "th04/main/pointnum/pointnum.hpp"
#include "th04/main/hud/overlay.hpp"
#include "th04/main/bullet/clearzap.hpp"
#include "th04/main/score.hpp"
#include "th04/resident.hpp"
#include "th04/math/vector.hpp"
#include "th04/snd/snd.h"
#include "compat/rec98/th02/main/item/shared.hpp"
#include "compat/rec98/th03/math/randring.hpp"

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
extern "C" void far sub_EFA1(void);
extern "C" void far sub_EEE8(void);

void far items_init(void)
{
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

void pascal far items_miss_add(void)
{
    int total_item_i;
    int field;
    int bigpower_index;
    int type;
    int unused_index;
    register item_t near *item;
    register int i;

    bigpower_index = randring2_next16_mod(ITEM_MISS_COUNT);
    do {
        unused_index = randring2_next16_mod(ITEM_MISS_COUNT);
    } while(unused_index == bigpower_index);

    if(player_pos.cur.x.v < TO_SP(PLAYFIELD_W / 3)) {
        field = MISS_FIELD_LEFT;
    } else if(player_pos.cur.x.v <= TO_SP((PLAYFIELD_W / 3) * 2)) {
        field = MISS_FIELD_CENTER;
    } else {
        field = MISS_FIELD_RIGHT;
    }

    i = 0;
    item = items;
    total_item_i = 0;
    while(total_item_i < ITEM_COUNT) {
        if(item->flag == F_FREE) {
            item->flag = F_ALIVE;
            item->unknown = 0;
            item->pos.cur.x.v = player_pos.cur.x.v;
            item->pos.cur.y.v = player_pos.cur.y.v;
            item->pos.velocity.y = ITEM_MISS_VELOCITIES[field][0][i];
            item->pos.velocity.x = ITEM_MISS_VELOCITIES[field][1][i];
            item->pulled_to_player = false;
            if(bigpower_index != i) {
                type = randring2_next16_and(IT_POINT);
            } else {
                type = IT_BIGPOWER;
            }
            if(resident->rem_lives == 1) {
                type = IT_FULLPOWER;
            }
            item->type = static_cast<unsigned char>(type);
            item->patnum = ITEM_PATNUM[type];
            i++;
            items_spawned++;
            if(i >= ITEM_MISS_COUNT) {
                return;
            }
        }
        total_item_i++;
        item++;
    }
}

static void pascal near item_collect(item_t near *item)
{
    register item_t near *p = item;
    bool yellow;
    register unsigned int points;

    yellow = false;

    switch(p->type) {
    case IT_POWER:
        if(power < POWER_MAX) {
            if(power == (POWER_MAX - 1)) {
                overlay_popup_show(POPUP_ID_FULL_POWERUP);
                bullets_clear();
            }
            power++;
            sub_11DE6();
            points = 1;
            break;
        }
        power_overflow++;
        if(static_cast<unsigned int>(power_overflow) >= POWER_OVERFLOW_MAX) {
            power_overflow = POWER_OVERFLOW_MAX;
            yellow = true;
        }
        points = POWER_OVERFLOW_BONUS[power_overflow];
        if(pointnum_times_2) {
            item_playperf_raise++;
        }
        break;

    case IT_POINT:
        if(p->pos.cur.y.v <= TO_SP(52)) {
            points = 5120;
            item_playperf_raise += 4;
            max_valued_point_items++;
            yellow = true;
            if(pointnum_times_2) {
                item_playperf_raise += 4;
            }
        } else {
            points = (3300 - (p->pos.cur.y.v / 2));
            item_playperf_raise += 2;
            if(pointnum_times_2) {
                item_playperf_raise += 2;
            }
        }
        total_point_items_collected++;
        points += dream_score;
        stage_point_items_collected++;
        hud_point_items_put();
        break;

    case IT_DREAM:
        if(dream_items_collected <= 6) {
            dream_items_collected++;
        }
        dream_score = DREAM_SCORE_PER_ITEMS[dream_items_collected];
        points = dream_score;
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
            sub_11DE6();
            points = 1;
            break;
        }
        power_overflow += 5;
        points = POWER_OVERFLOW_BONUS[power_overflow];
        if(static_cast<unsigned int>(power_overflow) > POWER_OVERFLOW_MAX) {
            power_overflow = POWER_OVERFLOW_MAX;
        }
        if(power_overflow == POWER_OVERFLOW_MAX) {
            points = 2560;
            yellow = true;
        }
        break;

    case IT_BOMB:
        resident->rem_bombs++;
        points = 100;
        sub_EFA1();
        break;

    case IT_1UP:
        playperf_raise(3);
        resident->rem_lives++;
        sub_EEE8();
        snd_se_play(7);
        overlay_popup_show(POPUP_ID_EXTEND);
        points = 100;
        break;

    case IT_FULLPOWER:
        bullets_clear();
        overlay_popup_show(POPUP_ID_FULL_POWERUP);
        power = POWER_MAX;
        sub_11DE6();
        points = 100;
        break;
    }

    if(pointnum_times_2 == false) {
        _EAX = points;
    } else {
        _AX = points;
        _AX += _AX;
        _EAX = _AX;
    }
    score_delta += _EAX;
    if(yellow == false) {
        pointnums_add_white(p->pos.cur.x.v, p->pos.cur.y.v, points);
    } else {
        pointnums_add_yellow(p->pos.cur.x.v, p->pos.cur.y.v, points);
    }
    if(item_playperf_raise >= 32) {
        item_playperf_raise -= 32;
        playperf_raise(1);
    }
    items_collected++;
}

static void pascal near item_lower_playperf(item_t near *item)
{
    register item_t near *p = item;

    switch(p->type) {
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
    if(item_playperf_lower >= 64) {
        item_playperf_lower -= 48;
        playperf_lower(1);
    }
}

void far items_update(void)
{
    unsigned char angle;
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
            item->flag = F_FREE;
            continue;
        }
        if(items_pull_to_player) {
            pointnum_times_2 = true;
            item->pulled_to_player = true;
            angle = iatan2(
                (player_pos.cur.y.v - item->pos.cur.y.v),
                (player_pos.cur.x.v - item->pos.cur.x.v)
            );
            vector2_near(item->pos.velocity, angle, TO_SP(ITEM_PULL_SPEED));
        } else if(item->pulled_to_player) {
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
            item->pos.velocity.x.v = 0;
        }

        if(miss_time == 0) {
            _BX = player_pos.cur.x.v;
            _BX += TO_SP(24);
            _BX -= _AX;
            if(_BX > TO_SP(48)) {
                goto no_collect;
            }
            _BX = player_pos.cur.y.v;
            _BX += TO_SP(24);
            _BX -= _DX;
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

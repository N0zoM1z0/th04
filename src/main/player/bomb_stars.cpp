#pragma option -zCMAIN__TEXT -zPmain_01
#include "x86real.h"
#include "compat/rec98/libs/master.lib/pc98_gfx.hpp"
#include "th04/math/vector.hpp"
#include "th04/math/randring.hpp"
#include "th04/main/playfld.hpp"
#include "th04/main/player/bomb.hpp"
#include "th04/playchar.h"
void pascal near z_super_put_16x16_mono_raw(int patnum);
#include "th04/sprites/main_pat.h"
static const int BOMB_STAR_COUNT = 48;
static const int BOMB_STAR_W = 16;
static const int BOMB_STAR_H = 16;
struct bomb_star_t { SPPoint center; unsigned char angle; SubpixelLength8 speed; };
extern bomb_star_t bomb_stars[BOMB_STAR_COUNT];
extern "C" void pascal near bomb_stars_update_and_render_for(int playchar)
{
    subpixel_t vector_x; subpixel_t vector_y;
    register bomb_star_t near *star; register int i;
    if(bomb_frame == 48) {
        star = bomb_stars; i = 0;
        for(; i < BOMB_STAR_COUNT; (i++, star++)) {
            star->center.x.v = randring1_next16_mod(PLAYFIELD_W * 16);
            star->center.y.v = randring1_next16_mod(PLAYFIELD_H * 16);
            if(playchar == PLAYCHAR_REIMU) {
                star->angle = -0x40;
                while((star->center.x.v >= ((PLAYFIELD_W / 3) * 16)) && (star->center.x.v <= (((PLAYFIELD_W / 3) * 2) * 16))) {
                    star->center.x.v = randring1_next16_mod(PLAYFIELD_W * 16);
                }
                star->speed.v = ((vector_x = (
                    (star->center.x.v <= ((PLAYFIELD_W / 2) * 16))
                    ? ((130 * 16) - star->center.x.v)
                    : (star->center.x.v + (-254 * 16))
                )) / 9);
            } else {
                star->angle = -0x20;
                star->speed.v = (randring1_next16_and((8 * 16) - 1) + (10 * 16));
            }
        }
    }
    star = bomb_stars; i = 0;
    for(; i < BOMB_STAR_COUNT; (i++, star++)) {
        vector2(vector_x, vector_y, star->angle, star->speed.v);
        star->center.x.v += vector_x; star->center.y.v += vector_y;
        if((star->center.x.v <= (-(BOMB_STAR_W / 2) * 16)) ||
           (star->center.x.v >= ((PLAYFIELD_W + (BOMB_STAR_W / 2)) * 16)) ||
           (star->center.y.v <= (-(BOMB_STAR_H / 2) * 16)) ||
           (star->center.y.v >= ((PLAYFIELD_H + BOMB_STAR_H) * 16))) {
            if(playchar == PLAYCHAR_REIMU) star->center.y.v = ((PLAYFIELD_H + BOMB_STAR_H) * 16);
            else if(i & 1) { star->center.x.v = (-8 * 16); star->center.y.v = randring1_next16_mod(PLAYFIELD_H * 16); }
            else { star->center.x.v = randring1_next16_mod(PLAYFIELD_W * 16); star->center.y.v = ((PLAYFIELD_H + (BOMB_STAR_H / 2)) * 16); }
        }
        _ES = SEG_PLANE_B;
        vector_x = ((star->center.x.v >> 4) + (PLAYFIELD_LEFT - (BOMB_STAR_W / 2)));
        _AX = ((star->center.y.v >> 4) + (PLAYFIELD_TOP - (BOMB_STAR_H / 2)));
        _CX = vector_x;
        z_super_put_16x16_mono_raw(120);
    }
}

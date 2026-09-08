#pragma option -zCMAIN_036_TEXT -zPmain_03
#include "compat/rec98/libs/master.lib/master.hpp"
#include "th04/sprites/main_pat.h"
#include "th04/main/frames.h"
#include "th04/main/boss/boss.hpp"
#include "th04/main/bullet/bullet.hpp"
#include "th04/main/bullet/laser_t.hpp"
#include "th04/main/custom.hpp"
#include "th04/main/player/player.hpp"
#include "th04/math/randring.hpp"
#include "th04/snd/snd.h"

static const int GENGETSU_SPAWNCOLUMN_COUNT = 16;

struct gengetsu_spawncolumn_t {
    signed char unused[2];
    PlayfieldPoint pos;
    signed char padding[20];
};

#define gengetsu_spawncolumns ( \
    reinterpret_cast<gengetsu_spawncolumn_t near *>(custom_entities) \
)

extern "C" unsigned char near gengetsu_phase_state(void);
extern "C" void near thicklaser_add(void);

extern "C" void near gengetsu_columns_phase(void)
{
    register gengetsu_spawncolumn_t near *column;
    register int i;
    unsigned char randomize;

    if(boss.phase_frame == 1) {
        randomize = randring2_next16_and(1);
        column = gengetsu_spawncolumns;
        for(i = 0; i < GENGETSU_SPAWNCOLUMN_COUNT; (i++, column++)) {
            if(randomize == 0) {
                column->pos.x.v = ((i * TO_SP(24)) + TO_SP(12));
            } else {
                column->pos.x.v = (
                    randring2_next16_mod(TO_SP(12)) +
                    ((i * TO_SP(24)) + TO_SP(6))
                );
            }
            column->pos.y.v = 0;
        }
    }

    switch(gengetsu_phase_state()) {
    case 1:
        bullet_template.spawn_type = BST_BULLET16;
        bullet_template.group = BG_SPREAD;
        bullet_template.count = 5;
        bullet_template.delta.spread_angle = 0x18;
        bullet_template.angle = -0x40;
        bullet_template.patnum = PAT_BULLET16_N_OUTLINED_BALL_WHITE;
        bullet_template.speed.v = (TO_SP(7) + 15);
        bullet_template_tune();
        bullets_add_regular();
        snd_se_play(3);
        boss_statebyte[15] = static_cast<unsigned char>(
            iatan2(
                (player_pos.cur.y.v - bullet_template.origin.y.v),
                (player_pos.cur.x.v - bullet_template.origin.x.v)
            ) - 0x30
        );
        break;

    case 2:
        thicklaser_template.origin.x.v = bullet_template.origin.x.v;
        thicklaser_template.origin.y.v = boss.pos.cur.y.v;
        thicklaser_template.radius_max = 64;
        thicklaser_template.radius_speed = 6;
        thicklaser_template.line_frames = 32;
        thicklaser_template.static_frames = 48;
        thicklaser_template.col_outline = 8;
        thicklaser_add();
        break;

    case 3:
        if(stage_frame_mod4 != 0) break;
        if(stage_frame_mod8 == 0) {
            bullet_template.spawn_type = BST_PELLET;
            bullet_template.angle = boss_statebyte[15];
            bullet_template.group = BG_STACK;
            bullet_template.count = 12;
            bullet_template.speed.v = TO_SP(2);
            bullet_template.delta.stack_speed.v = 8;
            boss_statebyte[15] += 0x0C;
            bullets_add_regular();
        }

        bullet_template.speed.v = TO_SP(8);
        bullet_template.angle = 0x40;
        bullet_template.patnum = PAT_BULLET16_N_OUTLINED_BALL_WHITE;
        bullet_template.spawn_type = BST_BULLET16;
        bullet_template.origin.y.v = 0;
        bullet_template.group = BG_SINGLE;
        column = gengetsu_spawncolumns;
        for(i = 0; i < GENGETSU_SPAWNCOLUMN_COUNT; (i++, column++)) {
            bullet_template.origin.x.v = column->pos.x.v;
            bullets_add_regular_fixedspeed();
        }
        snd_se_play(3);
        break;

    case 4:
        boss.phase_frame = 0;
        boss.mode = -1;
        break;
    }
}

#pragma option -zCMAIN_033_TEXT -zPmain_03

#include "th04/main/enemy/enemy.hpp"
#include "th04/formats/std.hpp"
#include "th04/main/rank.hpp"
#include "compat/rec98/th03/math/randring.hpp"

extern "C" void pascal near enemies_add(
    int script,
    subpixel_t center_x,
    subpixel_t center_y,
    unsigned char item
)
{
    register subpixel_t x = center_x;
    register enemy_t near *enemy = enemies;
    int i;

    for(i = 0; i < ENEMY_COUNT; i++, enemy++) {
        if(enemy->flag != EF_FREE) {
            continue;
        }

        enemy->flag = EF_ALIVE_FIRST_FRAME;
        enemy->cur_instr_frame = 0;
        enemy->loop_i = 0;
        enemy->age = 0;
        enemy->script_ip = 0;
        enemy->script = reinterpret_cast<unsigned char near *>(
            std_enemy_scripts[script]
        );

        if(x == (999 << 4)) {
            x = randring2_next16_mod(TO_SP(PLAYFIELD_W));
        }
        if(center_y == (999 << 4)) {
            center_y = randring2_next16_mod(TO_SP(PLAYFIELD_H));
        }

        enemy->pos.cur.x.v = x;
        enemy->pos.cur.y.v = center_y;
        enemy->item = static_cast<item_type_t>(item);
        enemy->damaged_this_frame = false;
        enemy->autofire = (rank == RANK_LUNATIC);
        enemy->clip_x = false;
        enemy->clip_y = false;
        enemy->anim_cels = 1;
        enemy->anim_frames_per_cel = 4;
        enemy->anim_cur_cel = 0;
        enemy->can_be_damaged = false;
        enemy->kills_player_on_collision = false;
        enemy->spawned_in_left_half = ((x < TO_SP(PLAYFIELD_W / 2))
            ? static_cast<unsigned char>(1)
            : static_cast<unsigned char>(0));
        enemy->autofire_cur_frame = randring2_next16();
        enemy->autofire_interval = 128;
        enemy->bullet_template.group = BG_FORCESINGLE_AIMED;
        enemy->bullet_template.spawn_type = BST_PELLET;
        enemy->bullet_template.speed.v = (TO_SP(2) + 10);
        enemy->bullet_template.origin.x.v = 0;
        enemy->bullet_template.origin.y.v = 0;
        return;
    }
}

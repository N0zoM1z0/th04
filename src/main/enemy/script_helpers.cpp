#pragma option -zCB4M_UPDATE_TEXT -zPmain_03

#include "th04/main/enemy/enemy.hpp"
#include "compat/rec98/th04/main/enemy/size.hpp"
#include "th04/main/player/player.hpp"
#include "th04/math/vector.hpp"
#include "compat/rec98/libs/master.lib/master.hpp"

extern unsigned int enemies_gone;

extern "C" unsigned char near enemy_pos_update(void)
{
    enemy_t near *enemy = enemy_cur;
    enemy->pos.update_seg3();

    if(enemy->clip_x && static_cast<unsigned int>(
        _AX + TO_SP(ENEMY_W / 2)
    ) >= TO_SP(PLAYFIELD_W + ENEMY_W)) {
        goto clip;
    }
    if(enemy->clip_y) {
        _DX += TO_SP(ENEMY_H / 2);
        if(static_cast<unsigned int>(_DX) >= TO_SP(PLAYFIELD_H + ENEMY_H)) {
            goto clip;
        }
    }
    return 0;

clip:
    enemies_gone++;
    enemy->flag = EF_KILLED;
    return 1;
}

extern "C" void near enemy_velocity_set(void)
{
    register enemy_t near *enemy = enemy_cur;
    vector2_near(enemy->pos.velocity, enemy->angle, enemy->speed.v);
}

extern "C" void near enemy_aim_at_player(void)
{
    register enemy_t near *enemy = enemy_cur;
    enemy->angle += iatan2(
        player_pos.cur.y.v - enemy->pos.cur.y.v,
        player_pos.cur.x.v - enemy->pos.cur.x.v
    );
    vector2_near(enemy->pos.velocity, enemy->angle, enemy->speed.v);
}

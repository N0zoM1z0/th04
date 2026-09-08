#pragma option -zCTILE_TEXT -zPmain_01
#pragma option -k-

#include "compat/rec98/th04/main/enemy/size.hpp"
#include "th04/main/enemy/enemy.hpp"
#include "th04/main/tile/tile.hpp"

extern "C" void pascal near tiles_invalidate_around(const SPPoint center);

void near enemies_invalidate(void)
{
    register enemy_t near *enemy;
    register int enemies_left;

    *reinterpret_cast<unsigned long near *>(&tile_invalidate_box) = (
        (static_cast<unsigned long>(ENEMY_W) << 16) | ENEMY_H
    );
    enemy = enemies;
    enemies_left = ENEMY_COUNT;
    do {
        if(
            (enemy->flag != EF_FREE) &&
            (enemy->flag != EF_ALIVE_FIRST_FRAME)
        ) {
            tiles_invalidate_around(enemy->pos.prev);
        }
        enemy++;
    } while(--enemies_left);
}

#pragma option -zCMAIN_033_TEXT -zPmain_03
#pragma option -G

#include "th04/main/enemy/enemy.hpp"

extern "C" void pascal near enemy_bullet_template_push(enemy_t near &enemy)
{
    bullet_template = enemy.bullet_template;
}

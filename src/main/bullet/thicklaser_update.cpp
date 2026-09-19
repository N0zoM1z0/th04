#pragma option -zCB4M_UPDATE_TEXT -zPmain_03

#include <mem.h>
#include "th04/main/bullet/laser_t.hpp"
#include "th04/main/player/player.hpp"

extern bool player_is_hit;
extern "C" void pascal far snd_se_play(int se);

void far thicklasers_init(void)
{
    register thicklaser_t near *laser = thicklasers;
    int i;

    for(i = 0; i < THICKLASER_COUNT; (i++, laser++)) {
        laser->flag = TF_FREE;
    }
    thicklaser_template.cur_flag_frame = 0;
    thicklaser_template.flag = TF_LINE;
    thicklaser_template.radius_cur = 1;
    thicklaser_template.radius_speed = 1;
}

// TH05 independently repeats this low-level copy order in two homologous
// helpers: word count, DS:ES, source/destination offsets, then REP MOVSW.
#pragma option -G
void near pascal thicklaser_template_pull(thicklaser_t near& laser)
{
    _CX = (sizeof(thicklaser_t) / sizeof(unsigned int));
    asm { push ds; pop es; }
    _SI = reinterpret_cast<unsigned int>(&thicklaser_template);
    _DI = reinterpret_cast<unsigned int>(&laser);
    asm { rep movsw; }
}

extern "C" void near thicklaser_add(void)
{
    register thicklaser_t near *laser = thicklasers;
    register int i;

    for(i = 0; i < THICKLASER_COUNT; (i++, laser++)) {
        if(laser->flag == TF_FREE) {
            thicklaser_template_pull(*laser);
            snd_se_play(5);
            break;
        }
    }
}

extern "C" void near thicklasers_update(void)
{
    register thicklaser_t near *laser = thicklasers;
    int i;
    register int radius;

    for(i = 0; i < THICKLASER_COUNT; (i++, laser++)) {
        if(laser->flag == TF_FREE) {
            continue;
        }
        if(laser->flag == TF_LINE) {
            if(laser->cur_flag_frame >= laser->line_frames) {
                laser->flag++;
                laser->cur_flag_frame = 0;
                snd_se_play(6);
            }
        } else if(laser->flag == TF_GROW) {
            laser->radius_cur += laser->radius_speed;
            if(laser->radius_cur >= laser->radius_max) {
                laser->flag++;
                laser->cur_flag_frame = 0;
                laser->radius_cur = laser->radius_max;
            }
        } else if(laser->flag == TF_STATIC) {
            if(laser->cur_flag_frame >= laser->static_frames) {
                laser->flag++;
                laser->cur_flag_frame = 0;
            }
        } else if(laser->flag == TF_SHRINK) {
            laser->radius_cur -= laser->radius_speed;
            if(laser->radius_cur <= 1) {
                laser->flag = TF_FREE;
            }
        }

        laser->cur_flag_frame++;
        if(static_cast<unsigned char>(laser->flag) <= TF_LINE) {
            continue;
        }

        radius = (laser->radius_cur << 3);
        if((laser->origin.y.v + radius) > player_pos.cur.y.v) {
            continue;
        }

        radius = (laser->radius_cur << 2);
        if(radius >= TO_SP(16)) {
            radius = TO_SP(16);
        }
        radius = ((laser->radius_cur << 4) - radius);
        if((laser->origin.x.v - radius) > player_pos.cur.x.v) {
            continue;
        }
        if((laser->origin.x.v + radius) < player_pos.cur.x.v) {
            continue;
        }
        player_is_hit = true;
    }
}

#pragma codeseg

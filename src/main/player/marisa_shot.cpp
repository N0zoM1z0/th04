#pragma option -zCMAIN_TEXT -zPmain_01
#pragma option -a

#include "x86real.h"
#include "src/main/player/shot.hpp"
#include "src/main/hardware/grcg.hpp"
#include "th04/main/scroll.hpp"
#include "th04/main/frames.h"
#include "th04/math/vector.hpp"
#include "th04/sprites/main_pat.h"

extern SPPoint player_option_pos_cur;
extern "C" void pascal near SHOT_LASER_PUT_RAW(void);

extern "C" void near shot_marisa_l0(void)
{
    Shot near *shot;
    shot_ptr = shots;
    shot_last_id = 0;
    if((shot = shots_add()) != 0) {
        shot->patnum_base = 0x22;
        shot->damage = 10;
    }
}

extern "C" void near shot_marisa_l1(void)
{
    Shot near *shot;
    shot_ptr = shots;
    shot_last_id = 0;
    if((shot = shots_add()) != 0) {
        shot_velocity_set(
            &shot->pos.velocity,
            static_cast<unsigned char>(randring1_next16_and(7)) - 0x44
        );
        shot->patnum_base = 0x22;
        shot->damage = 10;
    }
}

void pascal near shot_laser_update(
    unsigned int frames, shot_laser_style_t style
)
{
    Shot near *shot;

    if(shot_laser_time == 0) {
        shot_laser_time = frames;
        shot_laser_style = style;
        shot_laser_bottomcenter.cur.x.v = player_option_pos_cur.x.v;
        shot_laser_bottomcenter.cur.y.v = player_option_pos_cur.y.v;
        shot_laser_bottomcenter.prev.x.v = player_option_pos_cur.x.v;
        shot_laser_bottomcenter.prev.y.v = player_option_pos_cur.y.v;
        shot_laser_ring_cycle = 0;
    }

    if(shot_laser_time >= (SHOT_LASER_COOLDOWN_FRAMES + 16)) {
        shot_laser_ring_cycle++;
        if(shot_laser_ring_cycle <= 4) {
            shot_ptr = shots;
            shot_last_id = 0;
            if((shot = shots_add()) != 0) {
                shot->patnum_base = PAT_SHOT_LASER_RING;
                shot->damage = 9;
                shot->pos.velocity.y.v = TO_SP(-18);
                shot->pos.cur.x.v = (player_option_pos_cur.x.v + TO_SP(-24));
            }
            if((shot = shots_add()) != 0) {
                shot->patnum_base = PAT_SHOT_LASER_RING;
                shot->damage = 9;
                shot->pos.velocity.y.v = TO_SP(-18);
                shot->pos.cur.x.v = (player_option_pos_cur.x.v + TO_SP(24));
            }
        } else if(shot_laser_ring_cycle >= 8) {
            shot_laser_ring_cycle = 0;
        }
    }
}

extern "C" void near shot_marisa_a_l2(void)
{
    Shot near *shot;
    shot_laser_update(64, SLS_2);
    shot_ptr = shots;
    shot_last_id = 0;
    while((shot = shots_add()) != 0) {
        shot_velocity_set(
            &shot->pos.velocity,
            static_cast<unsigned char>(randring1_next16_and(7)) - 0x44
        );
        shot->patnum_base = 0x22;
        shot->damage = 9;
        break;
    }
}

extern "C" void near shot_marisa_a_l3(void)
{
    int shot_count = 2;
    Shot near *shot;
    shot_laser_update(72, SLS_2);
    shot_ptr = shots;
    shot_last_id = 0;
    while((shot = shots_add()) != 0) {
        if(shot_count == 2) {
            shot->pos.cur.x.v -= TO_SP(8);
        } else {
            shot->pos.cur.x.v += TO_SP(8);
        }
        shot->patnum_base = 0x22;
        shot->damage = 9;
        if(--shot_count <= 0) {
            break;
        }
    }
}

extern "C" void near shot_marisa_a_l4(void)
{
    int shot_count = 2;
    Shot near *shot;
    shot_laser_update(88, SLS_4);
    shot_ptr = shots;
    shot_last_id = 0;
    while((shot = shots_add()) != 0) {
        if(shot_count == 2) {
            shot->pos.cur.x.v -= TO_SP(8);
        } else {
            shot->pos.cur.x.v += TO_SP(8);
        }
        shot->patnum_base = 0x22;
        shot->damage = 9;
        if(--shot_count <= 0) {
            break;
        }
    }
}

extern "C" void near shot_marisa_a_l5(void)
{
    int shot_count = 3;
    unsigned char angle;
    Shot near *shot;
    shot_laser_update(104, SLS_4);
    angle = -0x48;
    shot_ptr = shots;
    shot_last_id = 0;
    while((shot = shots_add()) != 0) {
        shot_velocity_set(&shot->pos.velocity, angle);
        shot->patnum_base = 0x22;
        shot->damage = 8;
        angle += 8;
        if(--shot_count <= 0) {
            break;
        }
    }
}

extern "C" void near shot_marisa_a_l6(void)
{
    int shot_count = 3;
    unsigned char angle;
    Shot near *shot;
    shot_laser_update(128, SLS_6);
    angle = -0x48;
    shot_ptr = shots;
    shot_last_id = 0;
    while((shot = shots_add()) != 0) {
        shot_velocity_set(&shot->pos.velocity, angle);
        shot->patnum_base = 0x22;
        shot->damage = 8;
        angle += 8;
        if(--shot_count <= 0) {
            break;
        }
    }
}

extern "C" void near shot_marisa_a_l7(void)
{
    int shot_count = 3;
    unsigned char angle;
    Shot near *shot;
    shot_laser_update(144, SLS_1_4_1);
    angle = -0x48;
    shot_ptr = shots;
    shot_last_id = 0;
    while((shot = shots_add()) != 0) {
        shot_velocity_set(&shot->pos.velocity, angle);
        shot->patnum_base = 0x22;
        shot->damage = 8;
        angle += 8;
        if(--shot_count <= 0) {
            break;
        }
    }
}

extern "C" void near shot_marisa_a_l8(void)
{
    int shot_count = 5;
    unsigned char angle;
    Shot near *shot;
    shot_laser_update(168, SLS_1_4_1);
    angle = -0x4C;
    shot_ptr = shots;
    shot_last_id = 0;
    while((shot = shots_add()) != 0) {
        shot_velocity_set(&shot->pos.velocity, angle);
        shot->patnum_base = 0x22;
        shot->damage = 7;
        angle += 6;
        if(--shot_count <= 0) {
            break;
        }
    }
}

extern "C" void near shot_marisa_a_l9(void)
{
    int shot_count = 5;
    unsigned char angle;
    Shot near *shot;
    shot_laser_update(192, SLS_8);
    angle = -0x4C;
    shot_ptr = shots;
    shot_last_id = 0;
    while((shot = shots_add()) != 0) {
        shot_velocity_set(&shot->pos.velocity, angle);
        shot->patnum_base = 0x22;
        shot->damage = 7;
        angle += 6;
        if(--shot_count <= 0) {
            break;
        }
    }
}

extern "C" void near shot_marisa_b_l2(void)
{
    int shot_count = 3;
    Shot near *shot;
    shot_ptr = shots;
    shot_last_id = 0;
    while((shot = shots_add()) != 0) {
        if(shot_count <= 1) {
            shot->patnum_base = 0x22;
            shot_velocity_set(
                &shot->pos.velocity,
                static_cast<unsigned char>(randring1_next16_and(7)) - 0x44
            );
            shot->damage = 10;
        } else {
            if(shot_count == 3) {
                shot->pos.cur.x.v -= TO_SP(24);
            } else {
                shot->pos.cur.x.v += TO_SP(24);
            }
            shot->patnum_base = 0x24;
            shot->pos.velocity.y.v = TO_SP(-16);
            shot->damage = 6;
        }
        if(--shot_count <= 0) {
            break;
        }
    }
}

extern "C" void near shot_marisa_b_l3(void)
{
    int shot_count = 4;
    Shot near *shot;
    shot_ptr = shots;
    shot_last_id = 0;
    while((shot = shots_add()) != 0) {
        if(shot_count <= 2) {
            if(shot_count == 2) {
                shot->pos.cur.x.v -= TO_SP(8);
            } else {
                shot->pos.cur.x.v += TO_SP(8);
            }
            shot->patnum_base = 0x22;
            shot->damage = 9;
        } else {
            if(shot_count == 4) {
                shot->pos.cur.x.v -= TO_SP(24);
            } else {
                shot->pos.cur.x.v += TO_SP(24);
            }
            shot->patnum_base = 0x24;
            shot->pos.velocity.y.v = TO_SP(-16);
            shot->damage = 6;
        }
        if(--shot_count <= 0) {
            break;
        }
    }
}

extern "C" void near shot_marisa_b_l4(void)
{
    int shot_count = 4;
    Shot near *shot;
    shot_ptr = shots;
    shot_last_id = 0;
    while((shot = shots_add()) != 0) {
        if(shot_count <= 2) {
            if(shot_count == 2) {
                shot->pos.cur.x.v -= TO_SP(8);
            } else {
                shot->pos.cur.x.v += TO_SP(8);
            }
            shot->patnum_base = 0x22;
            shot->damage = 9;
        } else {
            if(shot_count == 4) {
                shot->pos.cur.x.v -= TO_SP(24);
            } else {
                shot->pos.cur.x.v += TO_SP(24);
            }
            shot->patnum_base = 0x24;
            vector2(
                shot->pos.velocity.x.v,
                shot->pos.velocity.y.v,
                static_cast<unsigned char>(randring1_next16_and(7)) - 0x44,
                TO_SP(16)
            );
            shot->damage = 6;
        }
        if(--shot_count <= 0) {
            break;
        }
    }
}

extern "C" void near shot_marisa_b_l5(void)
{
    int shot_count = 5;
    unsigned char angle = -0x48;
    Shot near *shot;
    shot_ptr = shots;
    shot_last_id = 0;
    while((shot = shots_add()) != 0) {
        if(shot_count <= 3) {
            shot->patnum_base = 0x22;
            shot_velocity_set(&shot->pos.velocity, angle);
            shot->damage = 9;
            angle += 8;
        } else {
            if(shot_count == 5) {
                shot->pos.cur.x.v -= TO_SP(24);
            } else {
                shot->pos.cur.x.v += TO_SP(24);
            }
            vector2(
                shot->pos.velocity.x.v,
                shot->pos.velocity.y.v,
                static_cast<unsigned char>(randring1_next16_and(7)) - 0x44,
                TO_SP(16)
            );
            shot->patnum_base = 0x24;
            shot->damage = 5;
        }
        if(--shot_count <= 0) {
            break;
        }
    }
}

extern "C" void near shot_marisa_b_l6(void)
{
    int shot_count = 7;
    subpixel_t x;
    unsigned char angle = -0x48;
    Shot near *shot;
    shot_ptr = shots;
    shot_last_id = 0;
    while((shot = shots_add()) != 0) {
        if(shot_count <= 3) {
            shot->patnum_base = 0x22;
            shot_velocity_set(&shot->pos.velocity, angle);
            shot->damage = 9;
            angle += 8;
        } else {
            switch(shot_count) {
            case 7: x = TO_SP(-32); break;
            case 6: x = TO_SP(-16); break;
            case 5: x = TO_SP(32); break;
            case 4: x = TO_SP(16); break;
            }
            shot->pos.cur.x.v -= x;
            shot->patnum_base = 0x24;
            shot->pos.velocity.y.v = TO_SP(-16);
            shot->damage = 5;
        }
        if(--shot_count <= 0) {
            break;
        }
    }
}

extern "C" void near shot_marisa_b_l7(void)
{
    int shot_count = 7;
    subpixel_t x;
    unsigned char angle = -0x4A;
    Shot near *shot;
    shot_ptr = shots;
    shot_last_id = 0;
    while((shot = shots_add()) != 0) {
        if(shot_count <= 3) {
            shot->patnum_base = 0x22;
            shot_velocity_set(&shot->pos.velocity, angle);
            shot->damage = 8;
            angle += 10;
        } else {
            switch(shot_count) {
            case 7: x = TO_SP(-32); break;
            case 6: x = TO_SP(-16); break;
            case 5: x = TO_SP(32); break;
            case 4: x = TO_SP(16); break;
            }
            shot->pos.cur.x.v -= x;
            shot->patnum_base = 0x24;
            shot->pos.velocity.y.v = TO_SP(-16);
            shot->damage = 5;
        }
        if(--shot_count <= 0) {
            break;
        }
    }
}

extern "C" void near shot_marisa_b_l8(void)
{
    int shot_count = 8;
    subpixel_t x;
    unsigned char angle = -0x4A;
    Shot near *shot;
    shot_ptr = shots;
    shot_last_id = 0;
    while((shot = shots_add()) != 0) {
        if(shot_count <= 4) {
            if(shot_count == 3) {
                shot->pos.cur.x.v -= TO_SP(8);
            } else if(shot_count == 2) {
                shot->pos.cur.x.v += TO_SP(8);
            }
            shot->patnum_base = 0x22;
            shot_velocity_set(&shot->pos.velocity, angle);
            shot->damage = 8;
            if(shot_count != 3) {
                angle += 10;
            }
        } else {
            switch(shot_count) {
            case 8: x = TO_SP(-32); break;
            case 7: x = TO_SP(-16); break;
            case 6: x = TO_SP(32); break;
            case 5: x = TO_SP(16); break;
            }
            shot->pos.cur.x.v -= x;
            shot->patnum_base = 0x24;
            shot->pos.velocity.y.v = TO_SP(-16);
            shot->damage = 5;
        }
        if(--shot_count <= 0) {
            break;
        }
    }
}

extern "C" void near shot_marisa_b_l9(void)
{
    int shot_count = 10;
    subpixel_t x;
    unsigned char angle = -0x4A;
    Shot near *shot;
    shot_ptr = shots;
    shot_last_id = 0;
    while((shot = shots_add()) != 0) {
        if(shot_count <= 4) {
            if(shot_count == 3) {
                shot->pos.cur.x.v -= TO_SP(8);
            } else if(shot_count == 2) {
                shot->pos.cur.x.v += TO_SP(8);
            }
            shot->patnum_base = 0x22;
            shot_velocity_set(&shot->pos.velocity, angle);
            shot->damage = 8;
            if(shot_count != 3) {
                angle += 10;
            }
        } else {
            switch(shot_count) {
            case 10: x = TO_SP(-48); break;
            case 9: x = TO_SP(-32); break;
            case 8: x = TO_SP(-16); break;
            case 7: x = TO_SP(48); break;
            case 6: x = TO_SP(32); break;
            case 5: x = TO_SP(16); break;
            }
            shot->pos.cur.x.v -= x;
            shot->patnum_base = 0x24;
            shot->pos.velocity.y.v = TO_SP(-16);
            shot->damage = 4;
        }
        if(--shot_count <= 0) {
            break;
        }
    }
}

extern "C" void near sub_E1F4(void)
{
    register int cel;
    if(shot_laser_time <= SHOT_LASER_COOLDOWN_FRAMES) {
        return;
    }

    switch(shot_laser_style) {
    case SLS_4:
        if(shot_laser_time <= (SHOT_LASER_COOLDOWN_FRAMES + 8)) {
            cel = SHOT_LASER_CEL_0;
            break;
        }
        cel = SHOT_LASER_CEL_1;
        break;

    case SLS_6:
        if(shot_laser_time <= (SHOT_LASER_COOLDOWN_FRAMES + 8)) {
            cel = SHOT_LASER_CEL_0;
            break;
        }
        if(shot_laser_time <= (SHOT_LASER_COOLDOWN_FRAMES + 16)) {
            cel = SHOT_LASER_CEL_1;
            break;
        }
        cel = SHOT_LASER_CEL_2;
        break;

    case SLS_1_4_1:
        if(shot_laser_time <= (SHOT_LASER_COOLDOWN_FRAMES + 8)) {
            cel = SHOT_LASER_CEL_0;
            break;
        }
        if(shot_laser_time <= (SHOT_LASER_COOLDOWN_FRAMES + 16)) {
            cel = SHOT_LASER_CEL_1;
            break;
        }
        if(shot_laser_time <= (SHOT_LASER_COOLDOWN_FRAMES + 24)) {
            cel = SHOT_LASER_CEL_2;
            break;
        }
        cel = SHOT_LASER_CEL_3;
        break;

    case SLS_8:
        if(shot_laser_time > (SHOT_LASER_COOLDOWN_FRAMES + 8)) {
            goto style_8_16;
        }
    case SLS_2:
    cel_0:
        cel = SHOT_LASER_CEL_0;
        goto cel_done;
    style_8_16:
        if(shot_laser_time > (SHOT_LASER_COOLDOWN_FRAMES + 16)) {
            goto style_8_24;
        }
    cel_1:
        cel = SHOT_LASER_CEL_1;
        goto cel_done;
    style_8_24:
        if(shot_laser_time > (SHOT_LASER_COOLDOWN_FRAMES + 24)) {
            goto cel_4;
        }
    cel_2:
        cel = SHOT_LASER_CEL_2;
        goto cel_done;
    cel_4:
        cel = SHOT_LASER_CEL_4;
    }
cel_done:

    _AL = stage_frame_mod2;
    _AL += 8;
    _AH = _AL;
    grcg_setcolor_direct_raw();

    _SI = shot_laser_bottomcenter.cur.y.v;
    _DX = scroll_subpixel_y_to_vram_seg1(TO_SP(PLAYFIELD_TOP));
    _AX = (
        (shot_laser_bottomcenter.cur.x.v >> 4) +
        ((PLAYFIELD_LEFT - PLAYER_OPTION_DISTANCE) - (SHOT_LASER_W / 2))
    );
    _BX = cel;
    SHOT_LASER_PUT_RAW();

    _SI = shot_laser_bottomcenter.cur.y.v;
    _DX = scroll_subpixel_y_to_vram_seg1(TO_SP(PLAYFIELD_TOP));
    _AX = (
        (shot_laser_bottomcenter.cur.x.v >> 4) +
        ((PLAYFIELD_LEFT + PLAYER_OPTION_DISTANCE) - (SHOT_LASER_W / 2))
    );
    _BX = cel;
    SHOT_LASER_PUT_RAW();
}

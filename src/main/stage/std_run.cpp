#pragma option -zCMAIN_033_TEXT -zPmain_03

#include "platform.h"
#include "th04/formats/std.hpp"
#include "th04/main/frames.h"
#include "th04/main/item/item.hpp"
#include "compat/rec98/th02/main/midboss/midboss.hpp"
#include "th04/main/null.hpp"

extern "C" void pascal near enemies_add(
    int script,
    subpixel_t center_x,
    subpixel_t center_y,
    unsigned char item
);

struct farptr_words_t {
    unsigned int offset;
    unsigned int segment;
};

#pragma pack(push, 1)
struct std_enemy_spawn_record_t {
    unsigned char script;
    subpixel_t center_x;
    subpixel_t center_y;
    unsigned char item;
    unsigned char unused[2];
};
#pragma pack(pop)

typedef char std_enemy_spawn_record_size_must_be_8[
    (sizeof(std_enemy_spawn_record_t) == 8) ? 1 : -1
];

#define std_ip_offset (reinterpret_cast<farptr_words_t near *>(&std_ip)->offset)

inline unsigned int std_byte_to_word(unsigned char value)
{
    return value;
}

void pascal far std_run(void)
{
    unsigned char spawn_count;

    if(*reinterpret_cast<unsigned int far *>(std_ip) != stage_frame) {
        return;
    }

    std_ip_offset += sizeof(unsigned int);
    spawn_count = *reinterpret_cast<unsigned char far *>(std_ip);
    std_ip_offset++;

    do {
        if(midboss_active == false) {
            #define spawn (*reinterpret_cast<std_enemy_spawn_record_t far *>(std_ip))
            enemies_add(
                spawn.script,
                spawn.center_x,
                spawn.center_y,
                std_byte_to_word(spawn.item)
            );
            #undef spawn
        }
        std_ip_offset += sizeof(std_enemy_spawn_record_t);
        spawn_count--;
    } while(spawn_count > 0);

    if(*reinterpret_cast<unsigned int far *>(std_ip) == 0) {
        stage_vm = nullfunc_far;
    }
}

#undef std_ip_offset

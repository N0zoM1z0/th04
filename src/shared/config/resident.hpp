#ifndef TH04_LOCAL_RESIDENT_HPP
#define TH04_LOCAL_RESIDENT_HPP

#include <stddef.h>

// TH04 resident block shared by ZUN.COM and MAIN.EXE. The byte layout is
// constrained by the decoded ZUN initializer and MAIN field accesses.
#define RES_ID "HUMAConfig"

typedef union {
    unsigned char continues_used;
    unsigned char digits[8];
} score_lebcd_t;

struct resident_t {
    char id[sizeof(RES_ID)];
    unsigned char rem_lives;
    unsigned char credit_lives;
    unsigned char rem_bombs;
    unsigned char credit_bombs;
    unsigned char rank;
    unsigned char bgm_mode;
    unsigned char stage;
    unsigned char playchar_ascii;
    char stage_ascii;
    long rand;
    unsigned char se_mode;
    char shottype;
    bool debug;
    short unused_1;
    score_lebcd_t score_last;
    char end_type_ascii;
    unsigned int std_frames;
    unsigned int items_spawned;
    unsigned int items_collected;
    unsigned int point_items_collected;
    unsigned int max_valued_point_items_collected;
    unsigned char end_sequence;
    unsigned char miss_count;
    unsigned char bombs_used;
    signed char unused_2;
    unsigned int enemies_gone;
    unsigned int enemies_killed;
    unsigned int graze;
    unsigned char cfg_lives;
    unsigned char cfg_bombs;
    unsigned char demo_stage;
    signed char unused_3;
    unsigned char demo_num;
    signed char unused_4;
    unsigned long slow_frames;
    unsigned long frames;
    bool zunsoft_shown;
    bool turbo_mode;
    signed char unused_5[182];
};

// Compile-time ABI checks under the pinned 16-bit TC4J profile.
typedef char th04_resident_size_check[(sizeof(resident_t) == 0x100) ? 1 : -1];
typedef char th04_resident_lives_check[(offsetof(resident_t, rem_lives) == 0x0B) ? 1 : -1];
typedef char th04_resident_debug_check[(offsetof(resident_t, debug) == 0x1A) ? 1 : -1];
typedef char th04_resident_frames_check[(offsetof(resident_t, frames) == 0x44) ? 1 : -1];

extern resident_t far *resident;

#endif

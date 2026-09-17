#ifndef TH04_LOCAL_CFG_HPP
#define TH04_LOCAL_CFG_HPP

#include <stddef.h>
#include "src/shared/config/resident.hpp"

// TH04's configuration file is ten bytes. ZUN.COM stores six option bytes,
// then a segment pointer, the debug flag, and their option checksum.
#define CFG_FN_LOWER "miko.cfg"

enum {
    CFG_LIVES_DEFAULT = 3,
    CFG_BOMBS_DEFAULT = 2
};

struct cfg_options_t {
    signed char rank;
    signed char lives;
    signed char bombs;
    signed char bgm_mode;
    signed char se_mode;
    signed char turbo_mode;
};

struct cfg_t {
    cfg_options_t opts;
    resident_t __seg *resident;
    signed char debug;
    signed char opts_sum;
};

typedef char th04_cfg_options_size_check[(sizeof(cfg_options_t) == 6) ? 1 : -1];
typedef char th04_cfg_size_check[(sizeof(cfg_t) == 10) ? 1 : -1];
typedef char th04_cfg_resident_check[(offsetof(cfg_t, resident) == 6) ? 1 : -1];
typedef char th04_cfg_debug_check[(offsetof(cfg_t, debug) == 8) ? 1 : -1];
typedef char th04_cfg_sum_check[(offsetof(cfg_t, opts_sum) == 9) ? 1 : -1];

#endif

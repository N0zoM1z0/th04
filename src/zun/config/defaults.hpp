#ifndef TH04_ZUN_CFG_DEFAULTS_HPP
#define TH04_ZUN_CFG_DEFAULTS_HPP

#include "src/shared/config/cfg.hpp"

// Target ZUN.COM's six-byte default options are FF 03 02 01 01 01.
enum {
    RANK_SHOW_SETUP_MENU = 0xFF,
    SND_BGM_FM26 = 1,
    SND_SE_FM = 1
};

#endif

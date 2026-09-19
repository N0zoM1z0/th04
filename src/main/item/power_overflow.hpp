#ifndef TH04_MAIN_ITEM_POWER_OVERFLOW_HPP
#define TH04_MAIN_ITEM_POWER_OVERFLOW_HPP

#include "src/shared/platform/types.hpp"

static const int POWER_OVERFLOW_MAX = 42;

// Score points granted for collecting power items while already at full power.
extern int16_t POWER_OVERFLOW_BONUS[POWER_OVERFLOW_MAX];

#endif

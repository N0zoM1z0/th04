#pragma once
#include "pmd_fm_effects.hpp"
namespace th04::portable::pmd {
struct MusicalLfo : FmLfo {
    std::int8_t depth_step=0;
    std::uint8_t depth_speed=0,initial_depth_speed=0;
    std::uint8_t depth_count=255,initial_depth_count=255,mask=0;
};
}

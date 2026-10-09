#pragma once
#include "pmd_fm_player.hpp"
#include <iosfwd>
namespace th04::portable::pmd {
// Diagnostic serialization only. Native state has no packed work offsets.
bool owns_fm_write(unsigned bank,unsigned address);
void write_fm_player_state(std::ostream&,const FmPlayer&);
void write_ssg_music_state(std::ostream&,const MusicalFm&,unsigned work_size);
}

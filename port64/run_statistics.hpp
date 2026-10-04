#pragma once
#include "application_state.hpp"
#include "item_system.hpp"
#include "score.hpp"

namespace th04::portable::gameplay {
// These counters belong to a MAIN executable lifetime, not to a Stage.
// STD increments before the actor prefix; total frames increments only when
// the frame tail completes. A nonreturning Ending call excludes that tail.
struct FrameCounts {
    std::uint16_t standard=0;
    std::uint32_t slow=0,total=0;
    void standard_tick() { ++standard; }
    void complete(std::uint16_t refreshes,std::uint16_t slowdown) {
        slow+=refreshes>=slowdown;
        ++total;
    }
};
application::RunStatistics run_statistics(
    const score::Snapshot& scoreboard,const item::ScoreState& items,
    std::uint16_t spawned,std::uint16_t enemies_gone,std::uint16_t enemies_killed,
    const FrameCounts& frames);
} // namespace th04::portable::gameplay

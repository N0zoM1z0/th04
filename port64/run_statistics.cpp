#include "run_statistics.hpp"

namespace th04::portable::gameplay {
application::RunStatistics run_statistics(
    const score::Snapshot& scoreboard,const item::ScoreState& items,
    std::uint16_t spawned,std::uint16_t enemies_gone,std::uint16_t enemies_killed,
    const FrameCounts& frames) {
    application::RunStatistics result;
    // GameExecl copies existing HUD digits before freeing MAIN. Pending delta
    // is deliberately excluded: draining it here would change the saved score.
    result.score_digits=scoreboard.digits;
    result.std_frames=frames.standard;
    result.items_spawned=spawned;
    result.items_collected=items.items_collected;
    result.point_items_collected=items.total_point_items_collected;
    result.max_valued_point_items_collected=items.max_valued_point_items;
    result.enemies_gone=enemies_gone;result.enemies_killed=enemies_killed;
    result.slow_frames=frames.slow;result.frames=frames.total;
    return result;
}
} // namespace th04::portable::gameplay

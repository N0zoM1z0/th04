#pragma once
#include <cstdint>
#include <string>
#include <vector>

namespace th04::portable::bonus {
// Values are MAIN/resident inputs, not host-width integers. Score deltas use
// ten-point units; only the displayed numeric gaiji append a final zero.
struct Context {
    std::uint8_t stage=0,resource_stage=0,rank=1,credit_lives=3,continues=0;
    std::uint8_t power=1,point_items=0,remaining_lives=3,misses=0,bombs_used=0;
    std::uint8_t defeated_in_time=1;
    std::uint16_t dream=0,graze=0;
};
struct State {
    std::uint32_t score_delta=0;
    std::uint8_t bombs=0,performance=16,minimum=11,maximum=24,extends=0;
    std::uint16_t palette_tone=100;
};
enum class Kind { tone,text,gaiji,raise_performance,lower_performance,hud_bombs };
struct Event {
    Kind kind{};
    int left=0,row=0,color=0;
    unsigned value=0;
    std::string bytes;
};
struct Result {
    std::uint32_t before_modifiers=0,awarded=0;
    std::vector<Event> events;
};
// all_clear includes the different Extra life multiplier and disables extends.
// Ordinary clear increments Bomb even when the timeout multiplier is zero.
Result apply(const Context&,State&,bool all_clear=false);
} // namespace th04::portable::bonus

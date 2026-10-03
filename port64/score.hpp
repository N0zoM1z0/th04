#pragma once
#include <array>
#include <cstdint>
#include <string>
#include <vector>

namespace th04::portable::score {
using Digits=std::array<std::uint8_t,8>;
struct Snapshot {
    // Little-endian decimal bytes. digits[0] stores continues, not points.
    // The highest byte deliberately retains the original unnormalized carry.
    Digits digits{},hiscore{},temporary{},hud{};
    std::uint32_t delta=0,frame_delta=0;
    std::uint8_t hiscore_popup_shown=0,unused=0,extends=0,lives=3;
    std::uint8_t bullet_clear=0,performance=16,minimum=11,maximum=24,popup_id=0;
    bool popup_callback=false;
};
enum class Kind { gaiji,performance_raise,hud_lives,sound };
struct Event { Kind kind{};unsigned left=0,row=0,value=0;std::string bytes; };
// Render requests are ordered with state changes. Native audio/HUD consumers
// can join without replacing score arithmetic or granting extra lives twice.
std::vector<Event> update(Snapshot&);
std::vector<Event> extend(Snapshot&);
std::vector<Event> render(Snapshot&);
std::uint32_t numeric_units(const Digits&); // debug ten-point units, ignores continues
} // namespace th04::portable::score

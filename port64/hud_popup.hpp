#pragma once
#include "registration_render.hpp"
#include <array>
#include <cstdint>

namespace th04::portable::popup {
enum class Kind : std::uint8_t { hiscore,extend,bonus,full_power };
struct Snapshot {
    std::uint8_t frame=0,current=0,requested=0;
    std::int16_t length=0,left=0,destination=0;
    bool reached=false,active=false;
    std::array<std::uint8_t,9> shift{};
    std::uint32_t bonus=0;
};
// Requests replace one pending ID. They do not reset an active popup's clock;
// the callback admits a different ID only after its first 64 updates.
void request(Snapshot&,Kind,std::uint32_t bonus=0);
void update(Snapshot&,registration::TextPlane&);
} // namespace th04::portable::popup

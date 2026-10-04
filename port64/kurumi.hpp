#pragma once
#include "orange.hpp"

namespace th04::portable::kurumi {
// The actual custom-entity view is six 26-byte records: byte flag, one
// retained byte, three signed point pairs, then twelve retained bytes.
struct Spawnray {
    std::uint8_t flag=0,unused=0;
    motion::Point target{},origin{},velocity{};
    std::array<std::uint8_t,12> padding{};
};
struct Snapshot {
    // BOSS, bonus, explosion and departure state have the same target owners
    // as Orange. Its patterns and custom entities belong to this system.
    orange::Snapshot boss{};
    std::array<Spawnray,6> rays{};
    std::uint8_t turn_toggle=0,unknown_state=0;
};
using Context=orange::Context;
using Event=orange::Event;
using EventType=orange::EventType;
using Sink=orange::Sink;
class System {
public:
    explicit System(unsigned rank=1);
    explicit System(Snapshot state):state_(state) {}
    const Snapshot& snapshot() const { return state_; }
    void update(const Context&,bullet::System&,gather::System&,spark::System&,
                randring::SharedRandomRing&,const Sink& sink={});
private:
    Snapshot state_{};
};
} // namespace th04::portable::kurumi

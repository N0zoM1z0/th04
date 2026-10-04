#pragma once
#include "midboss.hpp"
#include "effects.hpp"

namespace th04::portable::midboss2 {
struct Snapshot {
    midboss::Snapshot actor{};
    // These three process bytes are outside the shared 22-byte actor record.
    std::uint8_t pattern=0,direction=1,patterns_done=0;
};
class System {
public:
    explicit System(Snapshot initial):state_(initial) {}
    const Snapshot& snapshot() const { return state_; }
    void activate(std::uint16_t frame);
    void reset();
    void update(const midboss::Context& context,bullet::System& bullets,
                gather::System& gathers,randring::SharedRandomRing& random,
                const midboss::Sink& sink={});
    void prepare_render(const midboss::Context& context);
    const std::vector<midboss::Draw>& draws() const { return draws_; }
    std::uint32_t score_delta() const { return score_delta_; }
private:
    Snapshot state_;
    std::vector<midboss::Draw> draws_;
    std::uint32_t score_delta_=0;
};
} // namespace th04::portable::midboss2

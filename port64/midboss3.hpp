#pragma once
#include "midboss.hpp"
#include "effects.hpp"
namespace th04::portable::midboss3 {
struct Snapshot {
    midboss::Snapshot actor{};
    std::uint8_t pattern=0,mirror=0,patterns_done=0;
};
class System {
public:
    explicit System(Snapshot initial):state_(initial) {}
    const Snapshot& snapshot() const { return state_; }
    void activate(std::uint16_t frame);
    void reset();
    void update(const midboss::Context&,bullet::System&,gather::System&,
                randring::SharedRandomRing&,const midboss::Sink& sink={});
    void prepare_render(const midboss::Context&);
    const std::vector<midboss::Draw>& draws() const { return draws_; }
    std::uint32_t score_delta() const { return score_delta_; }
private:
    Snapshot state_;
    std::vector<midboss::Draw> draws_;
    std::uint32_t score_delta_=0;
};
} // namespace th04::portable::midboss3

#pragma once
#include "midboss.hpp"

namespace th04::portable::midbossx {
// Extra's hp word is an orbit radius. This owner never tests shots or grants
// a kill bonus; drops and the phase6 exit are scheduled by its own clock.
class System {
public:
    explicit System(midboss::Snapshot initial):state_(initial) {}
    const midboss::Snapshot& snapshot() const {return state_;}
    void activate(std::uint16_t frame);
    void reset();
    void update(const midboss::Context&,bullet::System&,randring::SharedRandomRing&,
                const midboss::Sink& sink={});
    void prepare_render(const midboss::Context&);
    const std::vector<midboss::Draw>& draws() const {return draws_;}
private:
    midboss::Snapshot state_;
    std::vector<midboss::Draw> draws_;
};
}

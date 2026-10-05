#pragma once
#include "cutscene_scene.hpp"
#include "verdict.hpp"

namespace th04::portable::verdict {
// Verdict owns graphics and its blocking clock, borrowing only immutable
// font/PI assets. Resident/RNG publication remains with MAINE's process owner.
class Scene {
public:
    Scene(const cutscene::Assets&,const Input&,std::array<Bytes,2> pages={},unsigned shown=0);
    void advance(std::uint16_t keys,const Sink& observer={});
    Status status() const { return script_.status(); }
    int tone() const { return script_.tone(); }
    unsigned ticks() const { return script_.ticks(); }
    std::size_t event_count() const { return script_.event_count(); }
    const Result& result() const { return script_.result(); }
    const cutscene::Canvas& canvas() const { return canvas_; }
private:
    void apply(const Event&);
    cutscene::Canvas canvas_;
    Script script_;
};
} // namespace th04::portable::verdict

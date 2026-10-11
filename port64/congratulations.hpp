#pragma once
#include "cutscene_scene.hpp"
#include "maine_animation.hpp"

namespace th04::portable::maine {
std::string congratulations_picture(unsigned playchar,unsigned rank);
std::vector<Request> congratulations_requests(unsigned playchar,unsigned rank);

// Owns the two transferred graphics pages and an immutable picture selection.
// No MAINE generation, score, resident value or random state changes here.
class Congratulations {
public:
    Congratulations(const cutscene::Assets&,unsigned playchar,unsigned rank,
                    std::array<Bytes,2> pages={},unsigned shown=0,vsync::RasterClock* clock=nullptr);
    void advance(std::uint16_t held,const RequestSink& observer={});
    std::uint64_t advance_elapsed(std::uint64_t,const KeySource&,const RequestSink& observer={},const ElapsedSink& service={});
    const cutscene::Canvas& canvas() const { return canvas_; }
    const Animation& animation() const { return animation_; }
    const std::string& picture_name() const { return picture_; }
private:
    void apply(const Request&,const RequestSink&);
    cutscene::Canvas canvas_;
    std::string picture_;
    Animation animation_;
};
} // namespace th04::portable::maine

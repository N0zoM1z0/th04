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
                    std::array<Bytes,2> pages={},unsigned shown=0);
    void advance(std::uint16_t held,const RequestSink& observer={});
    const cutscene::Canvas& canvas() const { return canvas_; }
    const Animation& animation() const { return animation_; }
    const std::string& picture_name() const { return picture_; }
private:
    cutscene::Canvas canvas_;
    std::string picture_;
    Animation animation_;
};
} // namespace th04::portable::maine

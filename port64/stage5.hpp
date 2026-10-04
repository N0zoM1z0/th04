#pragma once
#include "midboss.hpp"
#include "orange.hpp"
#include <functional>
#include <vector>

namespace th04::portable::stage5 {
// Stage5 installs null midboss callbacks. The retained actor is still storage,
// but it must never dispatch a Stage4 callback when the frame reaches 60000.
struct Setup {
    orange::Snapshot boss;
    midboss::Snapshot midboss;
    std::array<motion::Subpixel,3> centers{5120,640,3040};
};
Setup prepare(orange::Snapshot previous_boss,midboss::Snapshot previous_midboss,unsigned rank);

struct StarDraw { int left=0,physical_top=0; };
struct StarInvalidation { motion::Point center{}; int width=96,height=80; };
struct Stars {
    std::array<motion::Subpixel,3> centers{5120,640,3040};
    // Each successful simulation frame advances the stars exactly once.
    // Repaint reads these requests; a blocked dialog never advances centers.
    std::vector<StarDraw> update(std::uint8_t boss_phase,int scroll_line,bool scroll_active);
    std::array<StarInvalidation,3> invalidations() const;
};

// Original ST04.CDG plane B is ORed into plane I (E000). It is not an opaque
// four-color blit: other color bits and existing I bits remain intact.
class StarPlane {
public:
    explicit StarPlane(const std::vector<std::uint8_t>& cdg);
    void raster(int left,int physical_top,unsigned display_line,
                const std::function<std::uint8_t(unsigned,unsigned)>& read,
                const std::function<void(unsigned,unsigned,std::uint8_t)>& write) const;
private:
    std::array<std::uint8_t,960> blue_{};
};
} // namespace th04::portable::stage5

#pragma once

#include <array>
#include <cstdint>
#include <string>
#include <vector>

using Bytes = std::vector<uint8_t>;

struct PiImage {
    unsigned width{}, height{};
    std::array<uint8_t, 48> palette{};
    Bytes pixels;
};

// Renders the source-derived OP main-menu layout with original PI/CD2 assets.
// A screenshot is deterministic; a window also accepts Up/Down/Enter/Esc.
void run_title(const PiImage& background, const Bytes& labels,
               const Bytes& cursors, const std::string& screenshot,
               bool window);

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

// Renders the source-derived OP main/options layout with original PI/CD2
// assets. Screenshots are deterministic; the window accepts arrows,
// Enter and Esc through the platform-independent menu state machine.
void run_title(const PiImage& background, const Bytes& numerals,
               const Bytes& labels, const Bytes& cursors,
               const std::string& screenshot,
               const std::string& options_screenshot, bool window);

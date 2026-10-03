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

struct MainAssets {
    Bytes reimu;
    Bytes marisa;
    Bytes items;
    Bytes enemies;
    Bytes stage_tiles;
    Bytes reimu_map_tiles, marisa_map_tiles, map, standard;
};

// Renders the source-derived OP main/options layout with original PI/CD2
// assets. Screenshots are deterministic; the window accepts arrows,
// Enter and Esc through the platform-independent menu state machine.
void run_title(const PiImage& background, const Bytes& numerals,
               const Bytes& labels, const Bytes& cursors,
               const PiImage& selection_background,
               const Bytes& portraits,
               const MainAssets& main_assets,
               const std::string& screenshot,
               const std::string& options_screenshot,
               const std::string& character_screenshot,
               const std::string& shot_screenshot,
               const std::string& handoff_screenshot,
               const std::string& main_screenshot,
               const std::string& shooting_screenshots,
               const std::string& combat_screenshots, bool window);

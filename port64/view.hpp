#pragma once

#include <array>
#include <cstdint>
#include <string>
#include <vector>
#include <map>
#include "pi_image.hpp"
#include "cutscene_scene.hpp"
#include "staff_roll.hpp"
#include "registration_scene.hpp"
#include "op_ranking.hpp"
#include "op_music.hpp"
#include "op_setup.hpp"
#include "pmd_resident.hpp"
#include "op_startup.hpp"

struct StageAssets {
    Bytes stage_tiles,boss_tiles,backdrop,transition,boss_faces,map_tiles,map,standard,stars;
    std::array<Bytes,2> dialog_scripts,bad_dialog_scripts;
};

struct MainAssets {
    th04::portable::cutscene::Assets ending;
    th04::portable::staff::Assets staff_roll;
    th04::portable::registration::GraphicsAssets registration;
    th04::portable::op_ranking::Assets ranking;
    th04::portable::op_music::Assets music;
    th04::portable::op_setup::Assets setup;
    th04::portable::op_startup::Assets startup;
    bool full_startup=false;
    std::string startup_checks;
    std::string natural_route_checks;
    std::array<Bytes,4> replays;
    std::string save_directory;
    std::string configuration_checks;
    std::string setup_checks;
    std::string sound_checks;
    std::string sound_scene_checks;
    bool capture_sound_scenes=false;
    Bytes main_effects;
    std::map<std::string,Bytes> sound_resources;
    std::optional<th04::portable::sound::PmdProfile> pmd_profile;
    std::string resident_sound_checks;
    bool muted=true;
    std::string window_trace;
    StageAssets stage2,stage3,stage5,stage6,extra;
    std::array<Bytes,2> extra_defeat_faces;
    Bytes gengetsu_backdrop,gengetsu_transition;
    std::array<StageAssets,2> stage4;
    Bytes reimu;
    Bytes marisa;
    Bytes items;
    std::array<Bytes,2> bomb_tiles,bomb_pictures;
    Bytes enemies;
    Bytes stage_tiles,boss_tiles;
    Bytes explosion_sprite,orange_background,orange_transition;
    std::array<Bytes,2> dialog_scripts,player_faces;
    Bytes boss_faces,gaiji,font_bitmap;
    std::map<std::string,Bytes> dialog_sprites;
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
               const std::string& combat_screenshots,
               const std::string& midboss_screenshots,
               const std::string& orange_screenshots,
               const std::string& dialog_screenshots,
               const std::string& stage2_screenshots,const std::string& kurumi_screenshots,const std::string& stage3_screenshots,const std::string& elly_screenshots,const std::string& stage4_screenshots,const std::string& reimu_screenshots,const std::string& marisa_screenshots,const std::string& stage5_screenshots,const std::string& yuuka5_screenshots,const std::string& stage6_screenshots,const std::string& ending_screenshots,const std::string& registration_checks, const std::string& gameover_checks,const std::string& score_route_checks,const std::string& bomb_checks,const std::string& extra_checks,const std::string& mugetsu_checks,const std::string& gengetsu_checks,const std::string& extra_clear_checks,const std::string& extra_maine_checks,const std::string& op_score_checks,const std::string& op_ranking_checks,const std::string& op_music_checks,const std::string& demo_checks, bool window);

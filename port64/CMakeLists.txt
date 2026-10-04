cmake_minimum_required(VERSION 3.16)
project(th04_port64 LANGUAGES CXX)

if(NOT CMAKE_SIZEOF_VOID_P EQUAL 8)
  message(FATAL_ERROR "TH04 port64 requires a 64-bit compiler")
endif()

add_library(
  th04-portable-core STATIC
  application_state.cpp
  bullet_geometry.cpp
  item_system.cpp
  item_pool.cpp
  motion.cpp
  player_motion.cpp
  player_shots.cpp
  main_state.cpp
  sprite_sheet.cpp
  stage_background.cpp
  stage_program.cpp
  enemy_system.cpp
  enemy_bullets.cpp
  effects.cpp
  midboss.cpp
  midboss2.cpp
  midboss3.cpp
  midboss4.cpp
  stage4.cpp
  stage5.cpp
  stage6.cpp
  thick_lasers.cpp
  yuuka5.cpp
  yuuka6.cpp
  yuuka6_attacks.cpp
  yuuka6_background.cpp
  yuuka6_foreground.cpp
  yuuka6_pixels.cpp
  yuuka6_core.cpp
  yuuka6_entities.cpp
  yuuka5_render.cpp
  marisa.cpp
  marisa_render.cpp
  reimu.cpp
  reimu_render.cpp
  elly.cpp
  kurumi.cpp
  kurumi_render.cpp
  orange.cpp
  orange_render.cpp
  circles.cpp
  dialog.cpp
  cutscene.cpp
  maine_ending.cpp
  staff_roll.cpp
  verdict.cpp
  run_statistics.cpp
  cutscene_scene.cpp
  pi_image.cpp
  stage_bonus.cpp
  score.cpp
  stage_transition.cpp
  stage_session.cpp
  menu_state.cpp
  random_lcg.cpp
  random_ring.cpp
  selection_state.cpp
)
target_compile_features(th04-portable-core PUBLIC cxx_std_17)
target_compile_definitions(th04-portable-core PUBLIC GAME=4)
target_include_directories(th04-portable-core PUBLIC "${CMAKE_CURRENT_SOURCE_DIR}/..")

add_executable(th04-port64 main.cpp view.cpp)
target_compile_features(th04-port64 PRIVATE cxx_std_17)
target_link_libraries(th04-port64 PRIVATE th04-portable-core)

add_executable(th04-port64-contracts contracts.cpp)
target_link_libraries(th04-port64-contracts PRIVATE th04-portable-core)
add_executable(th04-port64-live-contracts live_contracts.cpp)
target_link_libraries(th04-port64-live-contracts PRIVATE th04-portable-core)
add_executable(th04-port64-shot-contracts shot_contracts.cpp)
target_link_libraries(th04-port64-shot-contracts PRIVATE th04-portable-core)
add_executable(th04-port64-enemy-contracts enemy_contracts.cpp)
target_link_libraries(th04-port64-enemy-contracts PRIVATE th04-portable-core)

add_executable(th04-port64-bullet-contracts bullet_contracts.cpp)
target_link_libraries(th04-port64-bullet-contracts PRIVATE th04-portable-core)

add_executable(th04-port64-effect-contracts effect_contracts.cpp)
target_link_libraries(th04-port64-effect-contracts PRIVATE th04-portable-core)
add_executable(th04-port64-midboss-contracts midboss_contracts.cpp)
target_link_libraries(th04-port64-midboss-contracts PRIVATE th04-portable-core)

add_executable(th04-port64-orange-contracts orange_contracts.cpp)
target_link_libraries(th04-port64-orange-contracts PRIVATE th04-portable-core)
add_executable(th04-port64-dialog-contracts dialog_contracts.cpp)
target_link_libraries(th04-port64-dialog-contracts PRIVATE th04-portable-core)
add_executable(th04-port64-cutscene-contracts cutscene_contracts.cpp staff_roll_contracts.cpp verdict_contracts.cpp)
target_link_libraries(th04-port64-cutscene-contracts PRIVATE th04-portable-core)

add_executable(th04-port64-bonus-contracts bonus_contracts.cpp)
target_link_libraries(th04-port64-bonus-contracts PRIVATE th04-portable-core)
add_executable(th04-port64-score-contracts score_contracts.cpp)
target_link_libraries(th04-port64-score-contracts PRIVATE th04-portable-core)

add_executable(th04-port64-transition-contracts transition_contracts.cpp)
target_link_libraries(th04-port64-transition-contracts PRIVATE th04-portable-core)

add_executable(th04-port64-session-contracts session_contracts.cpp)
target_link_libraries(th04-port64-session-contracts PRIVATE th04-portable-core)

add_executable(th04-port64-midboss2-contracts midboss2_contracts.cpp)
target_link_libraries(th04-port64-midboss2-contracts PRIVATE th04-portable-core)

add_executable(th04-port64-kurumi-contracts kurumi_contracts.cpp)
target_link_libraries(th04-port64-kurumi-contracts PRIVATE th04-portable-core)

add_executable(th04-port64-midboss3-contracts midboss3_contracts.cpp)
target_link_libraries(th04-port64-midboss3-contracts PRIVATE th04-portable-core)

add_executable(th04-port64-elly-contracts elly_contracts.cpp)
target_link_libraries(th04-port64-elly-contracts PRIVATE th04-portable-core)

add_executable(th04-port64-midboss4-contracts midboss4_contracts.cpp)
target_link_libraries(th04-port64-midboss4-contracts PRIVATE th04-portable-core)

add_executable(th04-port64-reimu-contracts reimu_contracts.cpp)
target_link_libraries(th04-port64-reimu-contracts PRIVATE th04-portable-core)

add_executable(th04-port64-marisa-contracts marisa_contracts.cpp)
target_link_libraries(th04-port64-marisa-contracts PRIVATE th04-portable-core)

add_executable(th04-port64-yuuka5-contracts yuuka5_contracts.cpp)
target_link_libraries(th04-port64-yuuka5-contracts PRIVATE th04-portable-core)

add_executable(th04-port64-laser-contracts laser_contracts.cpp)
target_link_libraries(th04-port64-laser-contracts PRIVATE th04-portable-core)

add_executable(th04-port64-stage5-contracts stage5_contracts.cpp)
target_link_libraries(th04-port64-stage5-contracts PRIVATE th04-portable-core)

add_executable(th04-port64-yuuka6-contracts yuuka6_contracts.cpp)
target_link_libraries(th04-port64-yuuka6-contracts PRIVATE th04-portable-core)

add_executable(th04-port64-yuuka6-entity-contracts yuuka6_entity_contracts.cpp)
target_link_libraries(th04-port64-yuuka6-entity-contracts PRIVATE th04-portable-core)

add_executable(th04-port64-yuuka6-attack-contracts yuuka6_attack_contracts.cpp)
target_link_libraries(th04-port64-yuuka6-attack-contracts PRIVATE th04-portable-core)

add_executable(th04-port64-yuuka6-core-contracts yuuka6_core_contracts.cpp)
target_link_libraries(th04-port64-yuuka6-core-contracts PRIVATE th04-portable-core)

add_executable(th04-port64-yuuka6-render-contracts yuuka6_render_contracts.cpp)
target_link_libraries(th04-port64-yuuka6-render-contracts PRIVATE th04-portable-core)

add_executable(th04-port64-yuuka6-background-contracts yuuka6_background_contracts.cpp)
target_link_libraries(th04-port64-yuuka6-background-contracts PRIVATE th04-portable-core)

foreach(target th04-portable-core th04-port64 th04-port64-contracts th04-port64-live-contracts th04-port64-shot-contracts th04-port64-enemy-contracts th04-port64-bullet-contracts th04-port64-effect-contracts th04-port64-midboss-contracts th04-port64-orange-contracts th04-port64-dialog-contracts th04-port64-cutscene-contracts th04-port64-bonus-contracts th04-port64-score-contracts th04-port64-transition-contracts th04-port64-session-contracts th04-port64-midboss2-contracts th04-port64-kurumi-contracts th04-port64-midboss3-contracts th04-port64-elly-contracts th04-port64-midboss4-contracts th04-port64-reimu-contracts th04-port64-marisa-contracts th04-port64-stage5-contracts th04-port64-laser-contracts th04-port64-yuuka5-contracts th04-port64-yuuka6-contracts th04-port64-yuuka6-entity-contracts th04-port64-yuuka6-attack-contracts th04-port64-yuuka6-core-contracts th04-port64-yuuka6-render-contracts th04-port64-yuuka6-background-contracts)
  if(MSVC)
    target_compile_options(${target} PRIVATE /W4)
  else()
    target_compile_options(${target} PRIVATE -Wall -Wextra -Wpedantic)
  endif()
endforeach()
if(MINGW)
  foreach(target th04-port64 th04-port64-contracts th04-port64-live-contracts th04-port64-shot-contracts th04-port64-enemy-contracts th04-port64-bullet-contracts th04-port64-effect-contracts th04-port64-midboss-contracts th04-port64-orange-contracts th04-port64-dialog-contracts th04-port64-cutscene-contracts th04-port64-bonus-contracts th04-port64-score-contracts th04-port64-transition-contracts th04-port64-session-contracts th04-port64-midboss2-contracts th04-port64-kurumi-contracts th04-port64-midboss3-contracts th04-port64-elly-contracts th04-port64-midboss4-contracts th04-port64-reimu-contracts th04-port64-marisa-contracts th04-port64-stage5-contracts th04-port64-laser-contracts th04-port64-yuuka5-contracts th04-port64-yuuka6-contracts th04-port64-yuuka6-entity-contracts th04-port64-yuuka6-attack-contracts th04-port64-yuuka6-core-contracts th04-port64-yuuka6-render-contracts th04-port64-yuuka6-background-contracts)
    target_link_options(${target} PRIVATE -static -static-libgcc -static-libstdc++)
  endforeach()
endif()
if(WIN32)
  target_link_libraries(th04-port64 PRIVATE user32 gdi32)
else()
  find_package(PkgConfig REQUIRED)
  pkg_check_modules(SDL2 REQUIRED IMPORTED_TARGET sdl2)
  target_link_libraries(th04-port64 PRIVATE PkgConfig::SDL2)
endif()

enable_testing()
add_test(NAME portable-contracts COMMAND th04-port64-contracts)
add_test(NAME live-main-contracts COMMAND th04-port64-live-contracts)
add_test(NAME player-shot-contracts COMMAND th04-port64-shot-contracts)
add_test(NAME stage-enemy-contracts COMMAND th04-port64-enemy-contracts)

add_test(NAME enemy-bullet-contracts COMMAND th04-port64-bullet-contracts)

add_test(NAME gameplay-effect-contracts COMMAND th04-port64-effect-contracts)
add_test(NAME stage1-midboss-contracts COMMAND th04-port64-midboss-contracts)

add_test(NAME stage1-orange-contracts COMMAND th04-port64-orange-contracts)
add_test(NAME dialog-contracts COMMAND th04-port64-dialog-contracts)

add_test(NAME stage-bonus-contracts COMMAND th04-port64-bonus-contracts)
add_test(NAME score-contracts COMMAND th04-port64-score-contracts)

add_test(NAME stage-transition-contracts COMMAND th04-port64-transition-contracts)

add_test(NAME stage-session-contracts COMMAND th04-port64-session-contracts)

add_test(NAME stage2-midboss-contracts COMMAND th04-port64-midboss2-contracts)

add_test(NAME stage2-kurumi-contracts COMMAND th04-port64-kurumi-contracts)

add_test(NAME stage3-midboss-contracts COMMAND th04-port64-midboss3-contracts)

add_test(NAME stage3-elly-contracts COMMAND th04-port64-elly-contracts)

add_test(NAME stage4-midboss-contracts COMMAND th04-port64-midboss4-contracts)

add_test(NAME stage4-reimu-contracts COMMAND th04-port64-reimu-contracts)

add_test(NAME marisa-core-contracts COMMAND th04-port64-marisa-contracts)

add_test(NAME stage5-contracts COMMAND th04-port64-stage5-contracts)

add_test(NAME thick-laser-contracts COMMAND th04-port64-laser-contracts)

add_test(NAME stage5-yuuka-contracts COMMAND th04-port64-yuuka5-contracts)

add_test(NAME stage6-yuuka-movement-contracts COMMAND th04-port64-yuuka6-contracts)

add_test(NAME stage6-yuuka-entity-contracts COMMAND th04-port64-yuuka6-entity-contracts)

add_test(NAME stage6-yuuka-attack-contracts COMMAND th04-port64-yuuka6-attack-contracts)

add_test(NAME stage6-yuuka-core-contracts COMMAND th04-port64-yuuka6-core-contracts)

add_test(NAME stage6-yuuka-foreground-contracts COMMAND th04-port64-yuuka6-render-contracts)

add_test(NAME stage6-yuuka-background-contracts COMMAND th04-port64-yuuka6-background-contracts)
add_test(NAME maine-cutscene-contracts COMMAND th04-port64-cutscene-contracts)

#pragma once
#include "item_system.hpp"
#include "score.hpp"
#include <functional>
#include <memory>
#include <vector>

namespace th04::portable::gameover {
enum class Kind {
    gaiji, ank, wipe, black, tone, delay, wait, continue_score, shot_level,
    hud_lives, hud_bombs, hud_score, song_fade, palette_fade, maine, bad_ending,
    score_sequence
};
struct Event {
    Kind kind{};int left=0,row=0,value=0,attribute=0;std::string text;
};
using Sink=std::function<void(const Event&)>;
struct Context {
    item::ScoreState& resources;
    score::Snapshot& scoreboard;
    std::uint8_t stage=0,credit_lives=3,credit_bombs=2;
    Sink sink;
    std::function<void()> save_continue;
};
// Same byte is retained from out to in. A successful final call does not wait.
bool fade_in(std::uint8_t& frame,const Sink&);
bool fade_out(std::uint8_t& frame,const Sink&);
enum class Choice { pending, continue_run, quit };
class Menu {
public:
    Menu(Context&,std::uint16_t initial_keys=0);
    void advance(std::uint16_t key_det);
    Choice choice() const {return choice_;}
    unsigned selected() const {return selected_;}
    std::uint16_t previous_input() const {return previous_input_;}
    std::uint32_t ticks() const {return ticks_;}
private:
    Context* context_;
    Choice choice_=Choice::pending;
    unsigned selected_=0;
    std::uint16_t previous_input_=1,previous_sample_=0;
    std::uint32_t ticks_=0;
};
enum class Phase {
    initial_out,initial_in,slide_in,slide_out,release,press,menu,
    final_out,final_in,blackout,continue_run,maine,bad_ending
};
// Blocking original Game Over is a refresh owner in the native process.
// MAIN actors/counters must remain suspended until this scene yields a route.
class Scene {
public:
    Scene(Context&,std::uint16_t initial_keys=0);
    void advance(std::uint16_t key_det);
    Phase phase() const {return phase_;}
    bool finished() const {return phase_>=Phase::continue_run;}
    std::uint32_t ticks() const {return ticks_;}
    int tone() const {return tone_;}
    unsigned selected() const {return menu_ ? menu_->selected() : 0;}
private:
    void pump(std::uint16_t held);
    Context* context_;
    Phase phase_=Phase::initial_out;
    std::uint8_t frame_=32;
    std::uint16_t previous_sample_=0;
    unsigned delay_=0;
    int slide_=50,tone_=100;
    unsigned fade_left_=0;
    std::uint32_t ticks_=0;
    bool slide_erase_=false,continued_=false,blackout_started_=false;
    std::unique_ptr<Menu> menu_;
};
} // namespace th04::portable::gameover

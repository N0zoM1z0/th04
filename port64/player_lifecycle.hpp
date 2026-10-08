#pragma once
#include "player_motion.hpp"
#include "player_shots.hpp"
#include "item_system.hpp"
#include <functional>
#include <optional>

namespace th04::portable::player {
// The host frontend's X/Enter/Esc masks differ from original MAIN key_det.
std::uint16_t input_from_host_actions(std::uint16_t);
enum class LifeKind {
    fire, miss_items, hud_dream, shot_level, sound, performance_lower,
    hud_lives, hud_bombs, game_over, bomb_tiles, character_bomb, scroll
};
struct LifeEvent { LifeKind kind{}; int value=0; };
using LifeSink=std::function<void(const LifeEvent&)>;
struct LifeState {
    std::uint8_t invincibility=64, hit=0, miss_time=0, respawn_time=0;
    std::uint16_t explosion_radius=0;
    std::uint8_t explosion_angle=0, misses=0, bombs_used=0, quit=0;
    std::uint8_t bombing=0, bomb_frame=0, bombing_disabled=0, clear_time=0;
    std::uint8_t pull_items=0, scroll_active=1, background=0, circle_color=13;
    std::uint16_t palette_tone=100;
    std::uint8_t palette_changed=0;
    std::array<std::uint8_t,3> palette14{}, palette_backup{};
    motion::Point options{}, previous_options{};
};
struct LifeContext {
    item::ScoreState& score;
    Movement& movement;
    shot::System& shots;
    std::uint8_t& performance;
    std::uint8_t minimum=11, credit_bombs=2;
    std::uint16_t scroll_line=0;
    LifeSink sink;
    // nullopt suspends the caller until resolve_game_over(). Required on the last-life path;
    // a missing consumer must never pretend that game-over completed.
    std::function<std::optional<std::uint8_t>()> game_over;
    std::function<void(LifeState&)> character_bomb;
};
// Original player_update prefix and miss/Bomb state producer. The fire and
// graphics requests are consumed at their actual call boundaries; shot entity
// movement, item pools and the blocking game-over scene remain separate owners.
class Lifecycle {
public:
    explicit Lifecycle(LifeState state={}):state_(state) {}
    const LifeState& state() const {return state_;}
    bool suspended() const {return suspended_;}
    void resolve_game_over(std::uint8_t quit);
    void latch_hit(bool hit) {if(hit)state_.hit=1;}
    void set_invincibility(std::uint8_t value) {state_.invincibility=value;}
    void set_bombing_disabled(std::uint8_t value) {state_.bombing_disabled=value;}
    void set_palette14(std::array<std::uint8_t,3> value) {state_.palette14=value;}
    void set_clear_time(std::uint8_t value) {state_.clear_time=value;}
    void synchronize_graphics(std::uint16_t tone,std::uint8_t color) {state_.palette_tone=tone;state_.circle_color=color;}
    void prepare_stage();
    void update(std::uint16_t key_det,bool shift,LifeContext&);
    void miss_update(LifeContext&);
    void bomb(LifeContext&);
    void render_bomb(LifeContext&);
private:
    LifeState state_;
    bool suspended_=false;
};
} // namespace th04::portable::player

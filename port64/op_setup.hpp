#pragma once
#include "cutscene_scene.hpp"
#include "sprite_sheet.hpp"
#include <deque>
#include <functional>

namespace th04::portable::op_setup {
struct Texts {
    std::array<std::string,2> captions;
    std::array<std::array<std::string,3>,2> choices;
    std::array<std::array<std::string,9>,2> help;
};
const Texts& texts();
enum class Kind {tone,super_load,access,load,palette,picture,free,copy,vsync,
    sprite,rectangle,text,reset,delay,sense,option,super_free};
struct Event {Kind kind;unsigned tick=0;int a=0,b=0,c=0,d=0;Bytes data;};
using Sink=std::function<void(const Event&)>;
struct Assets {cutscene::Assets graphics;Bytes windows;};
const char* kind_name(Kind);
// The two input samples straddle one refresh. input_reset_sense samples and
// clears the latch; the subsequent input_sense ORs into that latch.
class Scene {
public:
    explicit Scene(Sink={},unsigned text_effect=2);
    void advance(std::uint16_t held) {advance(held,held);}
    void advance(std::uint16_t before,std::uint16_t after);
    bool finished() const {return phase_==Phase::stopped;}
    bool awaiting_input() const {return phase_==Phase::release || phase_==Phase::press;}
    unsigned submenu() const {return submenu_;}
    unsigned selected() const {return selection_;}
    unsigned bgm() const {return bgm_;}
    unsigned se() const {return se_;}
    unsigned ticks() const {return tick_;}
    int tone() const {return tone_;}
    unsigned window_width() const {return width_;}
    unsigned window_height() const {return height_;}
private:
    enum class Phase {tasks,release,press,post_press,stopped};
    void emit(Kind,int=0,int=0,int=0,int=0,Bytes={});
    void queue(std::function<void()>);
    void drain();
    void wait(Kind);
    void fade(bool);
    void begin_submenu(unsigned);
    void singleline(int,int,unsigned);
    void dropdown(int,int,unsigned,unsigned);
    void rollup(int,int,unsigned,unsigned);
    void choice(unsigned,unsigned);
    void release();
    void input_wait(Phase);
    void controls();
    Sink sink_;
    std::deque<std::function<void()>> tasks_;
    Phase phase_=Phase::tasks;
    unsigned tick_=0,waiting_=0,width_=0,height_=0,submenu_=0,selection_=2,bgm_=2,se_=1,effect_=2;
    std::uint16_t before_=0,after_=0,latch_=0;
    int tone_=0;
};
class Renderer {
public:
    explicit Renderer(const Assets&);
    void apply(const Event&);
    const cutscene::Canvas& canvas() const {return canvas_;}
    Bytes rgb(int tone) const;
private:
    cutscene::Canvas canvas_;
    std::unique_ptr<sprite::Sheet> windows_;
    const Assets& assets_;
};
}

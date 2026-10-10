#pragma once
#include "pi_image.hpp"
#include "motion.hpp"
#include "random_lcg.hpp"
#include "sprite_sheet.hpp"
#include <deque>
#include <functional>
#include <memory>
#include <optional>

namespace th04::portable::op_startup {
using Palette=std::array<std::uint8_t,48>;
struct Pyro {
    std::uint8_t alive=0,age=0;
    motion::Point origin{};
    std::int16_t previous_distance=0,distance=0,speed=0;
    std::uint8_t angle=0,pattern=0;
};
struct Assets {PiImage logo,menu;std::array<PiImage,6> slides;std::array<Bytes,4> fireworks;};
enum class Kind {access,show,load,palette,picture,free,copy,clear,fill,snap,restore,
    bg_free,super_load,super_free,sprite,song,command,measure,reset,sense,wait,
    palette_show,se,se_update,logo_complete,complete};
struct Event {Kind kind;unsigned tick=0;int a=0,b=0,c=0;Bytes data;};
using Sink=std::function<void(const Event&)>;
const char* kind_name(Kind);
// The original treats a missing/inactive BGM driver as the frame fallback
// (zero for the logo). An active driver supplies its actual song measure.
using Measure=std::function<std::optional<std::uint16_t>()>;
class Scene {
public:
    Scene(const Assets&,bool logo,bool demo,Sink={},Measure={},std::uint32_t seed=rng::Lcg32::default_seed,std::uint16_t initial_held=0,Palette initial_palette={});
    void advance(std::uint16_t held);
    bool finished() const {return finished_;}
    unsigned ticks() const {return tick_;}
    unsigned logo_frame() const {return logo_frame_;}
    std::uint32_t random_state() const {return random_.state();}
    const std::array<Pyro,256>& pyros() const {return pyros_;}
    const Palette& palette() const {return palette_;}
    int tone() const {return tone_;}
private:
    void emit(Kind,int=0,int=0,int=0,Bytes={});
    void queue(std::function<void()>);
    void drain();
    void wait(unsigned);
    void fade(bool,unsigned,std::function<void()>);
    void palette_show();
    void apply_palette(const PiImage&,unsigned);
    void start_logo();
    void logo_ready();
    void run_logo_frame();
    void finish_logo();
    void start_title();
    void slide_frame();
    void title_flash();
    void monochrome_frame();
    void color_frame();
    void spawn(int y,int x,unsigned count,unsigned pattern);
    void update_pyros();
    const Assets& assets_;Sink sink_;Measure measure_;rng::Lcg32 random_;
    std::deque<std::function<void()>> tasks_;
    std::array<Pyro,256> pyros_{};Palette palette_{},logo_palette_{};
    unsigned tick_=0,waiting_=0,logo_frame_=0,slide_frame_=0,cel_=0,page_=0,fade_frame_=0;
    std::uint16_t held_=0;
    int tone_=0;std::uint8_t fade_in_=0,fade_out_=100,white_=0;
    bool demo_=false,skip_=false,measure_wait_=false,finished_=false;
};
// Owns PI slots, both indexed pages and the retained PI header palettes after
// free. DAC writes publish palette changes; loading BFNT only changes raw RGB.
class Renderer {
public:
    explicit Renderer(const Assets&);
    void apply(const Event&);
    const Bytes& page(unsigned p) const {return pages_.at(p);}
    const Palette& dac() const {return dac_;}
    unsigned shown() const {return shown_;}
    unsigned accessed() const {return accessed_;}
    Bytes rgb() const;
private:
    const Assets& assets_;std::array<Bytes,2> pages_;Bytes background_;
    std::array<const PiImage*,6> loaded_{};
    std::vector<std::unique_ptr<sprite::Sheet>> sheets_;
    Palette dac_{};unsigned shown_=0,accessed_=0;
};
}

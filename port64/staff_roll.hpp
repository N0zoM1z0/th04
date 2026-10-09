#pragma once
#include "pi_image.hpp"
#include <functional>
#include <map>
#include <optional>
#include <string>

namespace th04::portable::staff {
enum class Kind {
    tone, access, show, pi_load, pi_palette, pi_put, pi_free, copy_page,
    snap, bg_free, bgm_control, bgm_load, fade, cdg_load, cdg_free,
    cdg_free_all, measure, bg_rect, cdg_put, plane, grcg_on, grcg_off, vsync
};
struct Event {
    Kind kind;
    int a=0,b=0,c=0,d=0;
    std::string name;
    Event(Kind k,int aa=0,int bb=0,int cc=0,int dd=0,std::string n={})
        :kind(k),a(aa),b(bb),c(cc),d(dd),name(std::move(n)) {}
};
using Sink=std::function<void(const Event&)>;
struct Dimensions { unsigned width,height; };
using Lookup=std::function<Dimensions(const std::string&)>;
const char* kind_name(Kind);

// Request producer for the entire original staffroll_animate and its seven
// helpers. Graphics and sound are explicit consumers, allowing the complete
// request order to be checked against independently executed original code.
class Script {
public:
    explicit Script(const Lookup&,std::uint8_t angle=0);
    const std::vector<Event>& requests() const { return events_; }
    std::uint8_t angle() const { return angle_; }
private:
    enum class Shape { radial, diagonal, axis };
    void emit(Kind,int=0,int=0,int=0,int=0,std::string={});
    void load(unsigned,unsigned,const Lookup&);
    void restore(int,int,unsigned,int);
    void draw(int,int,int);
    void dissolve(int,int,bool);
    void two(int,int,int,int);
    std::vector<Event> events_;
    std::array<Dimensions,6> slots_{};
    unsigned slot_=0;
    std::uint8_t angle_;
    Shape shape_=Shape::radial;
};

struct Assets {
    std::map<std::string,PiImage> pictures;
    std::map<std::string,Bytes> sprites;
};
enum class Status { running, delay, measure, stopped };

// Staff Roll owns both graphics pages and one full-screen background snapshot.
// Keys do not skip these transitions. Active audio needs an actual measure;
// the inactive backend uses the original fallback frame count.
class Scene {
public:
    Scene(const Assets&,std::array<Bytes,2> pages={},unsigned shown=0);
    void advance(const Sink& observer={});
    void report_song_measure(std::uint16_t measure) { measure_=measure; }
    void set_audio_active(bool active) { audio_active_=active; }
    using MeasureSource=std::function<std::optional<std::uint16_t>()>;
    void set_measure_source(MeasureSource source) {measure_source_=std::move(source);}
    Status status() const { return status_; }
    const Bytes& page(unsigned p) const { return pages_.at(p); }
    const std::array<std::uint8_t,48>& palette() const { return palette_; }
    unsigned shown_page() const { return shown_; }
    unsigned access_page() const { return access_; }
    int tone() const { return tone_; }
    std::size_t event_count() const { return next_; }
    std::size_t ticks() const { return clock_; }
    bool background_alive() const { return !background_.empty(); }
    unsigned live_slots() const;
    const std::vector<Event>& sound_requests() const { return sound_; }
    // Bounded graphics consumer, also used for direct original-kernel controls.
    void apply(const Event&);
private:
    const Assets* assets_;
    Script script_;
    std::array<Bytes,2> pages_;
    std::array<const Bytes*,6> slots_{};
    const PiImage* loaded_=nullptr;
    Bytes background_;
    std::array<std::uint8_t,48> palette_{};
    std::vector<Event> sound_;
    unsigned shown_=0,access_=0;
    std::size_t next_=0,clock_=0;
    int tone_=100,left_=0,fade_step_=0,fade_goal_=100,fade_speed_=0;
    std::uint16_t measure_goal_=0;
    std::optional<std::uint16_t> measure_;
    MeasureSource measure_source_;
    bool audio_active_=false;
    Status status_=Status::running;
};
} // namespace th04::portable::staff

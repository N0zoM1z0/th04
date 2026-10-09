#pragma once
#include "cutscene_scene.hpp"
#include "motion.hpp"
#include "score_file.hpp"
#include <deque>

namespace th04::portable::op_music {
using Byte=score_file::Byte;
using Bytes=score_file::Bytes;
using Point=motion::Point;
struct Polygon {Point center{},velocity{};Byte angle=0,angle_speed=0;};
struct State {
    std::array<Polygon,16> polygons{};
    bool initialized=false;
    Byte playing=0,selected=0,page=1,comment_shown=0;
    std::array<Byte,800> comment{};
    unsigned text_effect=2;
};
enum class Kind { cdg_free,text_clear,tone,show,access,clear,load,palette,picture,free,copy,
    background_snap,background_rect,background_free,blue_snap,blue_restore,blue_free,
    grcg,text,polygon,delay,poll,sound,song,file,fade,vsync };
struct Event {Kind kind;unsigned tick=0;int a=0,b=0,c=0,d=0;Bytes data;};
using Sink=std::function<void(const Event&)>;
struct Assets {cutscene::Assets graphics;Bytes comments;};
// Process-local polygon/playing state survives Music Room visits. A scene
// owns its blocking input, animated comments, page flips and final blackout.
class Scene {
public:
    Scene(State&,const Assets&,score_file::Random,Sink={});
    void advance(std::uint16_t held);
    unsigned ticks() const {return ticks_;}
    int tone() const {return tone_;}
    bool finished() const {return stopped_;}
    const State& state() const {return state_;}
private:
    void emit(Kind,int=0,int=0,int=0,int=0,Bytes={});
    void access(int);
    void track(unsigned,unsigned);
    void comment();
    void comment_load(unsigned);
    void animate();
    void transition(unsigned);
    void queue(std::function<void()>);
    void drain(std::uint16_t);
    void controls(std::uint16_t);
    void finish_controls();
    void fade();
    State& state_;
    const Assets& assets_;
    score_file::Random random_;
    Sink sink_;
    std::deque<std::function<void()>> tasks_;
    enum class Phase {entry_release,controls,release,fade,stopped} phase_=Phase::entry_release;
    unsigned ticks_=0,fade_ticks_=0;
    int tone_=0;
    bool waiting_=false,stopped_=false;
    std::uint16_t sampled_=0;
};
void update_polygons(State&,const score_file::Random&,const std::function<void(const std::vector<Point>&)>&);
const std::array<std::string,24>& titles();
const std::array<std::string,22>& songs();
// Actual OP uses two edge DDAs with per-edge half-unit rounding, resets them
// at vertices, clips the first intersection before rounding, and includes
// the final scanline. A pixel-center intersection fill gives different edges.
void paint_polygon(Bytes&,const std::vector<Point>&);
class Renderer {
public:
    Renderer(const Assets&,std::array<Bytes,2> pages={},unsigned shown=0);
    void apply(const Event&);
    const cutscene::Canvas& canvas() const {return canvas_;}
    Bytes rgb(int tone) const;
private:
    cutscene::Canvas canvas_;
    Bytes blue_,background_;
};
const char* kind_name(Kind);
}

#pragma once
#include "op_score.hpp"
#include "cutscene_scene.hpp"
#include "sprite_sheet.hpp"

namespace th04::portable::op_ranking {
enum class Kind { sound,song,fade,vsync,tone,poll,delay,file,load,palette,picture,free,access,copy,name,gaiji,sprite };
struct Event {
    Kind kind;
    unsigned tick=0;
    int a=0,b=0,c=0,d=0;
    score_file::Bytes data;
};
using Sink=std::function<void(const Event&)>;
using FileSink=std::function<void(const score_file::Operation&)>;
enum class Phase { entry_out,entry_in,poll,left_in,right_in,exit_out,exit_in,release,stopped };
// OP SCORE0A74:2354..24A2 owns one blocking caller. It retains the startup
// score buffers and process RNG. Both arrow tests consume the SAME sample,
// including when the left page's black-in waits eighteen refreshes.
class Scene {
public:
    Scene(op_score::State&,score_file::File&,score_file::Byte configured_rank,
          score_file::Random,FileSink={},Sink={});
    void advance(std::uint16_t held);
    Phase phase() const {return phase_;}
    bool finished() const {return phase_==Phase::stopped;}
    unsigned ticks() const {return ticks_;}
    int tone() const {return tone_;}
    const op_score::Snapshot& snapshot() const {return state_.snapshot();}
private:
    void emit(Kind,int=0,int=0,int=0,int=0,score_file::Bytes={});
    void fade(Phase);
    void after_fade(std::uint16_t);
    void poll(std::uint16_t,Phase=Phase::poll);
    void right(std::uint16_t);
    void browse(int,Phase);
    void load();
    void render();
    op_score::State& state_;
    score_file::File& file_;
    score_file::Random random_;
    FileSink file_sink_;
    Sink sink_;
    score_file::Byte configured_;
    Phase phase_=Phase::entry_out;
    unsigned ticks_=0,fade_ticks_=0;
    int tone_=100;
    std::uint16_t sampled_=0;
};
struct Assets {
    cutscene::Assets graphics;
    score_file::Bytes numerals,rank_labels;
};
// Graphics requests use OP's GAMEFT, SCNUM and HI_M banks. MAINE's
// registration has different colors, columns and numeral patterns.
class Renderer {
public:
    Renderer(const Assets&,std::array<score_file::Bytes,2> pages={},unsigned shown=0);
    void apply(const Event&);
    const cutscene::Canvas& canvas() const {return canvas_;}
    score_file::Bytes rgb(unsigned page,int tone) const;
private:
    cutscene::Canvas canvas_;
    sprite::Sheet numerals_,labels_;
};
const char* kind_name(Kind);
} // namespace th04::portable::op_ranking

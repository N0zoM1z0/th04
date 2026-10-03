#pragma once
#include "motion.hpp"
#include <functional>
#include <string>
#include <vector>
#include <utility>

namespace th04::portable::dialog {
using Bytes=std::vector<std::uint8_t>;
inline bool stage_gate(std::uint8_t scroll_speed,std::uint8_t page_back) { return scroll_speed==0 && page_back==1; }
enum class Kind { box,text,gaiji,face_clear,face,sprite,clean,sprite_load,cdg_free,delay,wait,tone,fade,bgm_load,bgm_control,se_force,scroll,overlay_wipe };
struct Event {
    Kind kind{};int a=0,b=0,c=0,d=0;std::string name;
    Event(Kind k=Kind::box,int aa=0,int bb=0,int cc=0,int dd=0):kind(k),a(aa),b(bb),c(cc),d(dd) {}
};
using Sink=std::function<void(const Event&)>;
enum class Status { idle,running,delay,release,press,stopped };
class Script {
public:
    explicit Script(Bytes bytes):bytes_(std::move(bytes)) {}
    void begin();
    void advance(std::uint16_t held,const Sink& sink);
    Status status() const { return status_; }
    std::size_t offset() const { return at_; }
    motion::Point cursor() const { return cursor_; }
    std::int16_t side() const { return side_; }
    std::int16_t number_default() const { return default_; }
    int tone() const { return tone_; }
private:
    std::uint8_t peek(unsigned ahead=0) const;
    std::uint8_t take();
    int number(int fallback);
    int number();
    int second();
    std::string filename();
    void stop_command(const Sink&);
    void op(unsigned,const Sink&);
    void delay(int frames,const Sink&,const std::vector<Event>& after={});
    Bytes bytes_;
    std::size_t at_=0;
    motion::Point cursor_{};
    std::int16_t side_=0,default_=0;
    Status status_=Status::idle;
    bool box_=false,stop_after_wait_=false;
    int ticks_=0,press_budget_=0,press_elapsed_=0,tone_=100;
    int fade_end_=100,fade_step_=0,fade_speed_=0;
    std::vector<Event> after_;
};
// A supplied PC-98 Anex86/FREECG98 2048x2048 monochrome font replaces the
// hardware character ROM. No font or game asset is compiled into the product.
class Font {
public:
    explicit Font(const Bytes& bitmap);
    bool pixel(std::uint16_t sjis,unsigned x,unsigned y) const;
    bool present() const { return !bytes_.empty(); }
private:
    Bytes bytes_;unsigned offset_=0;
};
} // namespace th04::portable::dialog

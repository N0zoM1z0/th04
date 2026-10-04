#pragma once
#include <cstdint>
#include <deque>
#include <functional>
#include <string>
#include <vector>

namespace th04::portable::cutscene {
using Bytes = std::vector<std::uint8_t>;
// This is MAINE's observed key_det ABI, not MAIN's portable action mask.
constexpr std::uint16_t input_cancel = 0x10;
enum class Kind {
    snap, restore, bg_free, show, access, clear, copy_page,
    text, gaiji, egc_begin, box_mask, egc_end, pic_mask, pic_copy,
    pi_free, pi_load, pi_palette, pi_put, quarter, clear_rect,
    delay, wait, measure, tone, fade, scroll,
    bgm_control, bgm_load, se_begin, se, se_end
};
struct Event {
    Kind kind;
    int a=0, b=0, c=0, d=0, e=0;
    std::string name;
    Event(Kind k, int aa=0, int bb=0, int cc=0, int dd=0, int ee=0)
        : kind(k), a(aa), b(bb), c(cc), d(dd), e(ee) {}
};
using Sink = std::function<void(const Event&)>;
enum class Status { idle, running, delay, release, press, measure, stopped };

// MAINE's cutscene owner differs from MAIN's dialogue owner. Text is drawn
// into graphics page1 without per-character waits. Only box/picture masks,
// explicit script pauses and palette fades advance the blocking clock.
class Script {
public:
    explicit Script(Bytes bytes);
    void begin();
    void advance(std::uint16_t held, const Sink& sink);
    // The sound owner must report actual song progress. This is not a
    // fabricated frame timeout for the original measure-based wait.
    void complete_measure_wait();
    Status status() const { return status_; }
    std::size_t offset() const { return at_; }
    std::int16_t x() const { return x_; }
    std::int16_t y() const { return y_; }
    std::int16_t interval() const { return interval_; }
    std::uint8_t color() const { return color_; }
    std::uint16_t weight() const { return weight_; }
    std::int16_t number_default() const { return default_; }
    int tone() const { return tone_; }
private:
    unsigned peek() const;
    unsigned take();
    int number(int fallback);
    int number();
    int second();
    std::string filename();
    void op(unsigned command);
    void box_animate();
    void box_restore();
    void cursor_advance();
    void queue(Event event) { requests_.push_back(std::move(event)); }
    Bytes bytes_;
    std::deque<Event> requests_;
    std::size_t at_=0;
    std::int16_t x_=80, y_=320, interval_=1, default_=0;
    std::uint8_t color_=15;
    std::uint16_t weight_=2;
    Status status_=Status::idle;
    bool fast_forward_=false, ending_=false;
    int ticks_=0, press_budget_=0, press_elapsed_=0, tone_=100;
    int fade_end_=100, fade_step_=0, fade_speed_=0;
};

// _ED[character][shot][ending].TXT. The ending digit comes from MAIN's
// resident end type: good='0', bad='1', independent of the difficulty.
std::string script_name(unsigned character, unsigned shot, bool bad);
const char* kind_name(Kind kind);
} // namespace th04::portable::cutscene

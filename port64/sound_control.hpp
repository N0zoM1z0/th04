#pragma once
#include <array>
#include <cstdint>
#include <functional>
#include <string>
#include <utility>

namespace th04::portable::sound {
// Requests to the resident-driver/file seam. A muted consumer may record these
// without opening an audio device. This owner does not synthesize PMD samples.
enum class Kind {interrupt,open,read,close,beep_file,beep};
struct Request {Kind kind;std::uint16_t a=0,b=0;std::string name;};
using Sink=std::function<void(const Request&)>;
struct State {
    std::uint8_t bgm=0,se=0,midi_possible=0,interrupt_if_midi=0x60;
    std::uint8_t playing=255,frame=0;
    std::array<std::uint8_t,13> filename{};
};
struct Drivers {bool pmd=false,mmd=false;std::uint16_t type_reply=0x00ff;};
class Control {
public:
    explicit Control(State state={},Sink sink={}):state_(state),sink_(std::move(sink)){}
    const State& state() const {return state_;}
    std::uint16_t determine(std::uint16_t requested_bgm,std::uint16_t requested_se,Drivers);
    // Preserve the original register result when BGM is off, rather than
    // pretending that the formal parameter was loaded into AX.
    std::uint16_t command(std::uint16_t argument,std::uint16_t incoming_ax,std::uint16_t driver_reply);
    void reset();
    void play(std::uint16_t effect);
    void update();
    void load(const std::array<std::uint8_t,13>& base,std::uint16_t function);
    static const std::array<std::uint8_t,17>& priorities();
    static const std::array<std::uint8_t,17>& durations();
private:
    State state_;Sink sink_;
    void emit(Kind,std::uint16_t a=0,std::uint16_t b=0,std::string name={}) const;
};
const char* kind_name(Kind);
}

#pragma once
#include <cstdint>
#include <string>
#include <vector>

namespace th04::portable::demo {
inline constexpr unsigned frames=4000;
struct Sample {
    std::uint16_t input=0;
    std::uint8_t shift=0;
    bool replaced=false,finished=false;
};
// MAIN 0AAF:0949..0997 reads input and shift from separate 4000-byte banks.
// Physical nonzero key_det aborts before either read. Shift alone is replaced.
class Replay {
public:
    explicit Replay(std::vector<std::uint8_t> bytes);
    Sample sample(std::uint16_t frame,std::uint16_t physical_input,std::uint8_t physical_shift) const;
    static std::string filename(unsigned number);
private:
    std::vector<std::uint8_t> bytes_;
};
// OP checks the previous signed SI before resetting/incrementing it from input.
// Option frames accumulate idle time but do not start a replay themselves.
class Idle {
public:
    bool tick(bool options,std::uint16_t input);
    std::int16_t count() const {return count_;}
private:
    std::int16_t count_=0;
};
std::uint16_t host_input(std::uint8_t replay_input);
// palette_black_out waits one refresh first, then speed between palette writes.
class Fade {
public:
    explicit Fade(unsigned speed);
    void advance();
    int tone() const {return index_<0 ? 100 : index_==17 ? 0 : 100-index_*6;}
    bool published() const {return index_>=0;}
    bool finished() const {return index_==17;}
    unsigned ticks() const {return ticks_;}
private:
    unsigned speed_,left_,ticks_=0;
    int index_=-1;
};
}

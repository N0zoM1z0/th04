#pragma once
#include "motion.hpp"
#include <array>
#include <vector>

namespace th04::portable::stage {
struct Spawn {
    std::uint8_t script = 0;
    motion::Point position{};
    std::uint8_t item = 255;
};

// Own the STD bytecode and scheduled waves without segmented pointers. Map
// order/speeds stay with Background; script IDs and frame words stay unchanged.
class Program {
public:
    using Bytes = std::vector<std::uint8_t>;
    explicit Program(const Bytes& standard);
    const Bytes& script(unsigned id) const;
    unsigned script_count() const { return script_count_; }
    std::vector<Spawn> run(std::uint16_t frame, bool midboss_active = false);
    bool stopped() const { return stopped_; }
    unsigned cursor() const { return cursor_; }
    std::uint16_t pending_frame() const { return stopped_ ? 0 : waves_[cursor_].frame; }
    // Original offsets are relative to the STD allocation (file byte 3).
    unsigned original_cursor() const;
    unsigned original_script_offset(unsigned id) const;
private:
    struct Wave { std::uint16_t frame = 0; unsigned offset = 0; std::vector<Spawn> spawns; };
    std::array<Bytes,32> scripts_{};
    std::array<unsigned,32> script_offsets_{};
    unsigned script_count_ = 0, cursor_ = 0, terminator_ = 0;
    bool stopped_ = false;
    std::vector<Wave> waves_;
};
} // namespace th04::portable::stage

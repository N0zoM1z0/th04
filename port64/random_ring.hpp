#pragma once

#include <array>
#include <cstddef>
#include <cstdint>

namespace th04::portable::randring {

// Portable owner of the one random ring shared by the historical randring1_*
// and randring2_* accessor families. The native port exposes one API so that
// callers cannot accidentally model those entry-point copies as two streams.
class SharedRandomRing {
public:
    static constexpr std::size_t size = 256;

    // next_byte() corresponds to one far Pascal IRand() result. TH04 stores
    // the first result at index 255 and continues downward through index 0.
    template <class NextByte>
    void fill(NextByte&& next_byte) {
        for (std::size_t index = size; index-- > 0;) {
            bytes_[index] = static_cast<std::uint8_t>(next_byte());
        }
        cursor_ = 0;
    }

    std::uint16_t next16();
    std::uint16_t next16_and(std::uint16_t mask);
    std::uint16_t next16_mod(std::uint16_t divisor);

    std::uint16_t cursor() const { return cursor_; }

private:
    std::uint16_t sample_and_advance();

    std::array<std::uint8_t, size> bytes_{};
    std::uint16_t cursor_ = 0;
};

} // namespace th04::portable::randring

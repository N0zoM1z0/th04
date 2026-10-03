#include "random_ring.hpp"

#include <stdexcept>

namespace th04::portable::randring {

void SharedRandomRing::fill(rng::Lcg32& generator) {
    fill([&generator]() { return generator.next_byte(); });
}

std::uint16_t SharedRandomRing::sample_and_advance() {
    const auto index = static_cast<std::uint8_t>(cursor_);
    const auto low = bytes_[index];

    // The DOS word load at index 255 crosses into the immediately adjacent
    // low cursor byte. Synthesize that value explicitly instead of depending
    // on array overrun or host structure layout.
    const auto high = (index == 0xff)
        ? index
        : bytes_[static_cast<std::size_t>(index) + 1];
    const auto sample = static_cast<std::uint16_t>(
        low | (static_cast<std::uint16_t>(high) << 8)
    );

    // Preserve the original byte-sized increment. The high cursor byte is
    // cleared by fill() and remains unchanged across the wrap from 255 to 0.
    const auto next = static_cast<std::uint8_t>(index + 1);
    cursor_ = static_cast<std::uint16_t>((cursor_ & 0xff00u) | next);
    return sample;
}

std::uint16_t SharedRandomRing::next16() {
    return sample_and_advance();
}

std::uint16_t SharedRandomRing::next16_and(std::uint16_t mask) {
    return static_cast<std::uint16_t>(sample_and_advance() & mask);
}

std::uint16_t SharedRandomRing::next16_mod(std::uint16_t divisor) {
    const auto sample = sample_and_advance();
    if (divisor == 0) {
        // DOS reaches DIV after advancing the shared cursor. Use a defined
        // host exception while preserving that state change.
        throw std::domain_error("random-ring modulo divisor is zero");
    }
    return static_cast<std::uint16_t>(sample % divisor);
}

} // namespace th04::portable::randring

#include "pi_image.hpp"
#include <stdexcept>

namespace {
void require(bool ok,const char* reason) { if(!ok) throw std::runtime_error(reason); }
}

class PiReader {
public:
    explicit PiReader(const Bytes& b) : bytes(b) {}
    uint8_t byte() {
        require(pos < bytes.size(), "truncated PI data");
        return bytes[pos++];
    }
    uint32_t bits(unsigned n) {
        uint32_t v = 0;
        while (n--) {
            if (!remaining) { pending = byte(); remaining = 8; }
            v = (v << 1) | ((pending >> 7) & 1);
            pending <<= 1; --remaining;
        }
        return v;
    }
    uint16_t be16() { const auto high = byte(); return uint16_t((high << 8) | byte()); }
    unsigned color(unsigned context) {
        unsigned base, width;
        if (bits(1)) { base = 0; width = 1; }
        else if (!bits(1)) { base = 2; width = 1; }
        else if (bits(1)) { base = 8; width = 3; }
        else { base = 4; width = 2; }
        unsigned index = (base + bits(width)) ^ 15u;
        const auto value = colors[context][index];
        for (unsigned at = index; at < 15; ++at) colors[context][at] = colors[context][at + 1];
        colors[context][15] = value;
        return value;
    }
    Bytes unpack(unsigned width, unsigned height) {
        for (unsigned c = 0; c < 16; ++c)
            for (unsigned i = 0; i < 16; ++i) colors[c][i] = uint8_t((c + i + 1) & 15);
        const auto first = color(0);
        const auto second = color(first);
        const uint8_t initial = uint8_t((first << 4) | second);
        const size_t total = size_t(width) * (height + 2) / 2;
        Bytes image(total, initial);
        size_t cursor = width;
        int previous = -1;
        while (cursor < total) {
            unsigned position = bits(2);
            if (position == 3) position += bits(1);
            if (int(position) == previous) {
                do {
                    const auto high = color(image[cursor - 1] & 15);
                    const auto low = color(high);
                    image[cursor++] = uint8_t((high << 4) | low);
                    require(cursor <= total, "PI literal exceeds image");
                    if (!bits(1)) break;
                } while (true);
                previous = -1;
                continue;
            }
            unsigned count_bits = 0;
            while (bits(1)) require(++count_bits <= 19, "PI run length too large");
            size_t length = (size_t(1) << count_bits) | bits(count_bits);
            require(length <= total - cursor, "PI run exceeds image");
            if (position == 0) {
                const uint8_t last = image[cursor - 1];
                if ((last >> 4) == (last & 15)) {
                    while (length--) image[cursor++] = last;
                } else {
                    const uint8_t before = image[cursor - 2];
                    unsigned phase = 0;
                    while (length--) { image[cursor++] = phase ? last : before; phase ^= 1; }
                }
            } else if (position == 1 || position == 2) {
                const size_t distance = position == 1 ? width / 2 : width;
                require(distance && cursor >= distance, "PI copy before image start");
                while (length--) { image[cursor] = image[cursor - distance]; ++cursor; }
            } else {
                require(width >= 3, "PI diagonal copy too narrow");
                const size_t pixels = position == 3 ? width - 1 : width + 1;
                const size_t distance = (pixels + 1) / 2;
                require(cursor >= distance, "PI diagonal copy before image start");
                while (length--) {
                    const uint8_t left = image[cursor - distance];
                    const uint8_t right = image[cursor - distance + 1];
                    image[cursor++] = uint8_t((left << 4) | (right >> 4));
                }
            }
            previous = int(position);
        }
        return Bytes(image.begin() + width, image.end());
    }
    size_t pos{};
private:
    const Bytes& bytes;
    uint8_t pending{};
    unsigned remaining{};
    std::array<std::array<uint8_t, 16>, 16> colors{};
};

PiImage decode_pi(const Bytes& data) {
    PiReader r(data);
    require(r.byte() == 'P' && r.byte() == 'i', "PI magic missing");
    while (r.byte() != 26) {}
    while (r.byte() != 0) {}
    const auto mode = r.byte();
    require(r.byte() == 0 && r.byte() == 0 && r.byte() == 4, "unsupported PI planes");
    for (unsigned i = 0; i < 4; ++i) r.byte();
    const auto extension = r.be16();
    for (unsigned i = 0; i < extension; ++i) r.byte();
    PiImage out;
    out.width = r.be16(); out.height = r.be16();
    require(out.width >= 3 && out.height && out.width % 2 == 0 &&
            size_t(out.width) * (out.height + 2) <= 2097088,
            "unsupported PI dimensions");
    require(!(mode & 0x80), "PI image lacks an embedded palette");
    for (auto& c : out.palette) c = r.byte();
    out.pixels = r.unpack(out.width, out.height);
    return out;
}


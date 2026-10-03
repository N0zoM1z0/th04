// Native 64-bit TH04 resource bring-up. No DOS executable or game assets are
// embedded: the caller supplies their own original HDI or loose PAR archive.
#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <iterator>
#include <stdexcept>
#include <string>
#include <vector>

#include "view.hpp"

static void require(bool ok, const char* reason) {
    if (!ok) throw std::runtime_error(reason);
}

static uint16_t le16(const Bytes& b, size_t p) {
    require(p <= b.size() && b.size() - p >= 2, "short LE16 field");
    return uint16_t(b[p] | (uint16_t(b[p + 1]) << 8));
}

static uint32_t le32(const Bytes& b, size_t p) {
    return uint32_t(le16(b, p)) | (uint32_t(le16(b, p + 2)) << 16);
}

static void put16(Bytes& b, size_t p, uint16_t v) {
    b[p] = uint8_t(v); b[p + 1] = uint8_t(v >> 8);
}

static void put32(Bytes& b, size_t p, uint32_t v) {
    put16(b, p, uint16_t(v)); put16(b, p + 2, uint16_t(v >> 16));
}

static Bytes read_file(const std::string& name) {
    std::ifstream in(name, std::ios::binary);
    require(bool(in), "cannot open input file");
    Bytes b((std::istreambuf_iterator<char>(in)), std::istreambuf_iterator<char>());
    require(!b.empty(), "empty input file");
    return b;
}

static void write_file(const std::string& name, const Bytes& b) {
    std::ofstream out(name, std::ios::binary);
    require(bool(out), "cannot open output file");
    out.write(reinterpret_cast<const char*>(b.data()), std::streamsize(b.size()));
    require(bool(out), "cannot write output file");
}

class Fat12 {
public:
    explicit Fat12(const Bytes& image) : b(image) {
        constexpr size_t p = 38912;
        require(b.size() >= p + 512, "short PC-98 HDI");
        sector = le16(b, p + 11);
        cluster_sectors = b[p + 13];
        const auto reserved = le16(b, p + 14);
        const auto fats = b[p + 16];
        const auto entries = le16(b, p + 17);
        const auto sectors = le16(b, p + 19);
        const auto fat_sectors = le16(b, p + 22);
        require(sector == 1024 && cluster_sectors == 8 && reserved == 1 &&
                fats == 2 && entries == 1536 && sectors == 20706 &&
                fat_sectors == 4, "unexpected TH04 FAT12 geometry");
        require(p + size_t(sectors) * sector <= b.size(), "FAT12 volume truncated");
        fat_start = p + size_t(reserved) * sector;
        const size_t fat_bytes = size_t(fat_sectors) * sector;
        require(std::equal(b.begin() + fat_start, b.begin() + fat_start + fat_bytes,
                           b.begin() + fat_start + fat_bytes), "FAT mirrors disagree");
        root = fat_start + size_t(fats) * fat_bytes;
        const size_t root_sectors = (size_t(entries) * 32 + sector - 1) / sector;
        data = root + root_sectors * sector;
        max_cluster = 1 + (sectors - reserved - fats * fat_sectors - root_sectors) / cluster_sectors;
    }

    Bytes op_archive() const {
        const size_t dir = find({root}, "GENSO      ");
        const auto dirs = chain(le16(b, dir + 26));
        std::vector<size_t> offsets;
        for (auto c : dirs) offsets.push_back(cluster_offset(c));
        // CP932 short name of the original OP/ending resource archive.
        const std::string op_name("\x8c\xb6\x91\x7a\x8b\xbd" "EDDAT", 11);
        const size_t file = find(offsets, op_name);
        return file_bytes(le16(b, file + 26), le32(b, file + 28));
    }

private:
    const Bytes& b;
    size_t sector{}, cluster_sectors{}, fat_start{}, root{}, data{}, max_cluster{};

    uint16_t next(uint16_t cluster) const {
        require(cluster >= 2 && cluster <= max_cluster, "FAT cluster out of range");
        uint16_t word = le16(b, fat_start + cluster + cluster / 2);
        return cluster & 1 ? (word >> 4) & 0xfff : word & 0xfff;
    }

    std::vector<uint16_t> chain(uint16_t first) const {
        std::vector<uint16_t> result;
        std::vector<bool> seen(max_cluster + 1);
        for (uint16_t c = first; c < 0xff8; c = next(c)) {
            require(c >= 2 && c <= max_cluster && !seen[c], "invalid FAT chain");
            seen[c] = true;
            result.push_back(c);
        }
        require(!result.empty(), "empty FAT chain");
        return result;
    }

    size_t cluster_offset(uint16_t c) const {
        require(c >= 2 && c <= max_cluster, "cluster out of range");
        const size_t at = data + (size_t(c) - 2) * sector * cluster_sectors;
        require(at <= b.size() && b.size() - at >= sector * cluster_sectors,
                "cluster outside image");
        return at;
    }

    size_t find(const std::vector<size_t>& dirs, const std::string& name) const {
        require(name.size() == 11, "FAT name must be 11 bytes");
        for (size_t start : dirs) {
            const size_t end = start + (start == root ? 1536 * 32 : sector * cluster_sectors);
            require(end <= b.size(), "directory outside image");
            for (size_t at = start; at < end; at += 32) {
                if (b[at] == 0) break;
                if (b[at] != 0xe5 && b[at + 11] != 0x0f &&
                    std::equal(name.begin(), name.end(), b.begin() + at,
                               [](char a, uint8_t c) { return uint8_t(a) == c; })) return at;
            }
        }
        throw std::runtime_error("GENSO or OP archive missing from HDI");
    }

    Bytes file_bytes(uint16_t first, size_t size) const {
        const auto clusters = chain(first);
        const size_t cluster_bytes = sector * cluster_sectors;
        require(size <= clusters.size() * cluster_bytes, "file exceeds FAT chain");
        Bytes out;
        out.reserve(size);
        for (uint16_t c : clusters) {
            const auto at = cluster_offset(c);
            const auto n = std::min(size - out.size(), cluster_bytes);
            out.insert(out.end(), b.begin() + at, b.begin() + at + n);
            if (out.size() == size) break;
        }
        return out;
    }
};

static Bytes archive_member(const Bytes& b, const std::string& wanted) {
    require(b.size() >= 16, "short PAR archive");
    const auto count = le16(b, 4);
    const auto table_size = le16(b, 0);
    require(count > 0 && table_size == (count + 1) * 32 &&
            16 + size_t(table_size) <= b.size() && le16(b, 6) <= 255,
            "invalid PAR directory");
    Bytes directory(b.begin() + 16, b.begin() + 16 + table_size);
    uint8_t key = uint8_t(le16(b, 6));
    for (auto& v : directory) {
        v ^= key;
        key = uint8_t(key - v);
    }
    require(std::all_of(directory.end() - 32, directory.end(),
                        [](uint8_t v) { return v == 0; }), "PAR terminal record changed");
    for (size_t i = 0; i < count; ++i) {
        const size_t at = i * 32;
        const auto first = directory.begin() + at + 3;
        const auto last = std::find(first, first + 13, 0);
        const std::string name(first, last);
        if (name != wanted) continue;
        const auto type = le16(directory, at);
        const auto aux = directory[at + 2];
        const size_t packed_size = le16(directory, at + 16);
        const size_t logical_size = le16(directory, at + 18);
        const size_t offset = le32(directory, at + 20);
        require(offset >= 16 + size_t(table_size) && offset <= b.size() &&
                packed_size <= b.size() - offset, "PAR member outside archive");
        Bytes out;
        int previous = -1;
        for (size_t p = offset; p < offset + packed_size; ++p) {
            uint8_t value = b[p] ^ aux;
            out.push_back(value);
            if (type == 0x9595 && value == previous) {
                require(++p < offset + packed_size, "PAR repeat count missing");
                const uint8_t repeats = b[p] ^ aux;
                out.insert(out.end(), repeats, value);
            }
            previous = value;
            require(out.size() <= logical_size + 1, "PAR expansion exceeds length");
        }
        require(type == 0xf388 || type == 0x9595, "unknown PAR compression");
        require(out.size() == logical_size || out.size() == logical_size + 1,
                "PAR expanded size disagrees with directory");
        out.resize(logical_size);
        return out;
    }
    throw std::runtime_error("PAR member missing: " + wanted);
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

static PiImage decode_pi(const Bytes& data) {
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

static uint32_t fnv32(const Bytes& b) {
    uint32_t hash = 2166136261u;
    for (auto v : b) hash = (hash ^ v) * 16777619u;
    return hash;
}

static Bytes bmp24(const PiImage& img) {
    const size_t stride = (size_t(img.width) * 3 + 3) & ~size_t(3);
    require(stride * img.height <= UINT32_MAX - 54, "BMP size overflow");
    Bytes bmp(54 + stride * img.height);
    bmp[0] = 'B'; bmp[1] = 'M';
    put32(bmp, 2, uint32_t(bmp.size()));
    put32(bmp, 10, 54); put32(bmp, 14, 40);
    put32(bmp, 18, img.width); put32(bmp, 22, img.height);
    put16(bmp, 26, 1); put16(bmp, 28, 24);
    put32(bmp, 34, uint32_t(stride * img.height));
    for (size_t y = 0; y < img.height; ++y) {
        const size_t row = 54 + (img.height - y - 1) * stride;
        for (size_t x = 0; x < img.width; ++x) {
            const uint8_t packed = img.pixels[y * img.width / 2 + x / 2];
            const unsigned color = x & 1 ? packed & 15 : packed >> 4;
            for (unsigned c = 0; c < 3; ++c)
                bmp[row + x * 3 + c] = uint8_t((img.palette[color * 3 + (2 - c)] >> 4) * 17);
        }
    }
    return bmp;
}

int main(int argc, char** argv) {
    try {
        std::string hdi, archive, member, output, title_screenshot;
        bool title_window = false;
        for (int i = 1; i < argc; ++i) {
            const std::string arg = argv[i];
            if (arg == "--title") { title_window = true; continue; }
            require(i + 1 < argc, "each option needs a value");
            const std::string value = argv[++i];
            if (arg == "--hdi") hdi = value;
            else if (arg == "--archive") archive = value;
            else if (arg == "--member") member = value;
            else if (arg == "--output") output = value;
            else if (arg == "--title-screenshot") title_screenshot = value;
            else throw std::runtime_error("unknown option: " + arg);
        }
        const bool title = title_window || !title_screenshot.empty();
        require((!hdi.empty()) != (!archive.empty()) && (title || !member.empty()) &&
                !(title && (!member.empty() || !output.empty())),
                "usage: th04-port64 (--hdi FILE | --archive FILE) "
                "[--member NAME --output BMP | --title [--title-screenshot BMP]]");
        const auto par = hdi.empty() ? read_file(archive) : Fat12(read_file(hdi)).op_archive();
        if (title) {
            const auto bg = decode_pi(archive_member(par, "OP1.PI"));
            run_title(bg, archive_member(par, "SFT2.CD2"),
                      archive_member(par, "CAR.CD2"), title_screenshot,
                      title_window);
            return 0;
        }
        const auto pi = decode_pi(archive_member(par, member));
        if (!output.empty()) write_file(output, bmp24(pi));
        std::cout << member << " " << pi.width << "x" << pi.height << " FNV32="
                  << std::uppercase << std::hex << std::setw(8) << std::setfill('0')
                  << fnv32(pi.pixels) << std::endl;
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "th04-port64: " << e.what() << std::endl;
        return 1;
    }
}

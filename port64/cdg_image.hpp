#pragma once
#include "pi_image.hpp"
#include <stdexcept>

// Read-only CDG/CD2 header and bottom-to-top planar pixel view. The file owns
// these bytes; a sheet must not outlive its source buffer. Header segment words
// describe DOS allocations and never become host pointers.
inline void require_cdg(bool ok,const char* reason) {
    if(!ok) throw std::invalid_argument(reason);
}
inline unsigned cdg_word(const Bytes& bytes,unsigned offset) {
    return unsigned(bytes.at(offset))|(unsigned(bytes.at(offset+1))<<8);
}
struct CdgSheet {
    enum Layout : uint8_t {
        colors_only = 0,
        alpha_and_colors = 1,
        alpha_only = 2,
    };

    explicit CdgSheet(const Bytes& source) : bytes(source) {
        require_cdg(bytes.size() >= 16, "short CD2 file");
        plane_size = cdg_word(bytes, 0);
        width = cdg_word(bytes, 2);
        height = cdg_word(bytes, 4);
        row_dwords = cdg_word(bytes, 8);
        image_count = bytes[10];
        layout = bytes[11];
        require_cdg(
            width && height && image_count && row_dwords &&
                size_t(row_dwords) * 4 * height == plane_size,
            "invalid CD2 geometry"
        );
        require_cdg(
            size_t(row_dwords) * 4 == (size_t(width) + 7) / 8,
            "unsupported CD2 row padding"
        );
        require_cdg(layout <= alpha_only, "unknown CD2 plane layout");
        planes_per_image = (layout == colors_only) ? 4 :
            ((layout == alpha_only) ? 1 : 5);
        image_size = size_t(plane_size) * planes_per_image;
        require_cdg(
            image_size <= bytes.size() - 16 &&
                size_t(image_count) <= (bytes.size() - 16) / image_size &&
                16 + size_t(image_count) * image_size == bytes.size(),
            "CD2 file size disagrees with header"
        );
    }

    bool bit(unsigned image, unsigned plane, unsigned x, unsigned y) const {
        require_cdg(
            image < image_count && plane < planes_per_image &&
                x < width && y < height,
            "CD2 pixel outside image"
        );
        // CD2 rows are stored from the bottom of the image toward the top,
        // matching the original renderer's decreasing PC-98 VRAM address.
        const size_t file_y = height - y - 1;
        const size_t offset = 16 + size_t(image) * image_size +
            size_t(plane) * plane_size +
            file_y * row_dwords * 4 + x / 8;
        return (bytes[offset] & (0x80u >> (x & 7))) != 0;
    }

    const Bytes& bytes;
    unsigned plane_size{};
    unsigned width{};
    unsigned height{};
    unsigned row_dwords{};
    unsigned image_count{};
    unsigned layout{};
    unsigned planes_per_image{};
    size_t image_size{};
};


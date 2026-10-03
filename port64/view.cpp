#include "view.hpp"
#include "application_state.hpp"
#include "menu_state.hpp"
#include "selection_state.hpp"
#include "main_state.hpp"
#include "sprite_sheet.hpp"
#include "stage_background.hpp"

#include <algorithm>
#include <cstddef>
#include <chrono>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <utility>
#include <memory>

#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#else
#include <SDL.h>
#endif

namespace {

namespace menu = th04::portable::menu;
namespace application = th04::portable::application;
namespace selection = th04::portable::selection;
namespace gameplay = th04::portable::gameplay;
namespace sprite = th04::portable::sprite;
namespace player = th04::portable::player;
namespace stage = th04::portable::stage;
namespace shot = th04::portable::shot;
namespace bullet = th04::portable::bullet;
namespace spark = th04::portable::spark;
namespace gather = th04::portable::gather;

using Clock = std::chrono::steady_clock;
// PC-98 640x400 cadence. Advance simulation independently of host redraw or
// key-repeat delivery. At most four overdue ticks are run before resync.
constexpr auto frame_period = std::chrono::nanoseconds(17730496);

constexpr unsigned choice_count = 6;
constexpr unsigned option_count = 8;
constexpr int label_width = 96;
constexpr int label_height = 16;
constexpr int cursor_width = 32;
constexpr int menu_top = 224;
constexpr int command_height = label_height + 4;
constexpr int command_left = (640 - label_width) / 2;
constexpr int cursor_left = command_left - cursor_width / 2;
constexpr int cursor_right = command_left + label_width - cursor_width / 2;
constexpr int option_left = (640 - label_width * 2) / 2;
constexpr int option_value_left = option_left + label_width;
constexpr int option_cursor_right = option_value_left + label_width - cursor_width;
constexpr unsigned color_inactive = 1;
constexpr unsigned color_active = 8;
constexpr unsigned color_locked = 12;
constexpr int portrait_width = 256;
constexpr int portrait_height = 244;
constexpr int portrait_top = 52;
constexpr int reimu_left = 48;
constexpr int marisa_left = 336;
constexpr int raised = 8;

void require_view(bool condition, const char* reason) {
    if (!condition) {
        throw std::runtime_error(reason);
    }
}

uint16_t le16(const Bytes& bytes, size_t offset) {
    require_view(
        offset <= bytes.size() && bytes.size() - offset >= 2,
        "short CD2 header"
    );
    return uint16_t(bytes[offset] | (uint16_t(bytes[offset + 1]) << 8));
}

void put16(Bytes& bytes, size_t offset, uint16_t value) {
    bytes[offset] = uint8_t(value);
    bytes[offset + 1] = uint8_t(value >> 8);
}

void put32(Bytes& bytes, size_t offset, uint32_t value) {
    put16(bytes, offset, uint16_t(value));
    put16(bytes, offset + 2, uint16_t(value >> 16));
}

struct Frame {
    unsigned width{};
    unsigned height{};
    std::vector<uint32_t> pixels;
};

struct CdgSheet {
    enum Layout : uint8_t {
        colors_only = 0,
        alpha_and_colors = 1,
        alpha_only = 2,
    };

    explicit CdgSheet(const Bytes& source) : bytes(source) {
        require_view(bytes.size() >= 16, "short CD2 file");
        plane_size = le16(bytes, 0);
        width = le16(bytes, 2);
        height = le16(bytes, 4);
        row_dwords = le16(bytes, 8);
        image_count = bytes[10];
        layout = bytes[11];
        require_view(
            width && height && image_count && row_dwords &&
                size_t(row_dwords) * 4 * height == plane_size,
            "invalid CD2 geometry"
        );
        require_view(
            size_t(row_dwords) * 4 == (size_t(width) + 7) / 8,
            "unsupported CD2 row padding"
        );
        require_view(layout <= alpha_only, "unknown CD2 plane layout");
        planes_per_image = (layout == colors_only) ? 4 :
            ((layout == alpha_only) ? 1 : 5);
        image_size = size_t(plane_size) * planes_per_image;
        require_view(
            image_size <= bytes.size() - 16 &&
                size_t(image_count) <= (bytes.size() - 16) / image_size &&
                16 + size_t(image_count) * image_size == bytes.size(),
            "CD2 file size disagrees with header"
        );
    }

    bool bit(unsigned image, unsigned plane, unsigned x, unsigned y) const {
        require_view(
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

uint32_t palette_color(const PiImage& image, unsigned index) {
    require_view(index < 16, "palette index outside image");
    const auto component = [&](unsigned channel) {
        return uint32_t((image.palette[index * 3 + channel] >> 4) * 17);
    };
    return 0xff000000u | (component(0) << 16) | (component(1) << 8) |
        component(2);
}

Frame background_frame(const PiImage& image) {
    require_view(
        image.width && image.height && image.width % 2 == 0 &&
            image.pixels.size() == size_t(image.width) * image.height / 2,
        "invalid decoded PI image"
    );
    Frame frame{image.width, image.height,
                std::vector<uint32_t>(size_t(image.width) * image.height)};
    for (size_t y = 0; y < image.height; ++y) {
        for (size_t x = 0; x < image.width; ++x) {
            const uint8_t packed = image.pixels[y * image.width / 2 + x / 2];
            const unsigned index = (x & 1) ? (packed & 15) : (packed >> 4);
            frame.pixels[y * image.width + x] = palette_color(image, index);
        }
    }
    return frame;
}

void put_indexed_pixel(
    Frame& frame, const PiImage& palette, int left, int top,
    unsigned x, unsigned y, unsigned color
) {
    const int screen_x = left + int(x);
    const int screen_y = top + int(y);
    if (
        screen_x >= 0 && screen_y >= 0 &&
        screen_x < int(frame.width) && screen_y < int(frame.height)
    ) {
        frame.pixels[size_t(screen_y) * frame.width + screen_x] =
            palette_color(palette, color);
    }
}

void put_monochrome(
    Frame& frame, const PiImage& palette, const CdgSheet& sheet,
    unsigned image, int left, int top, unsigned color
) {
    require_view(sheet.layout == CdgSheet::alpha_only, "CD2 is not a mask sheet");
    for (unsigned y = 0; y < sheet.height; ++y) {
        for (unsigned x = 0; x < sheet.width; ++x) {
            if (sheet.bit(image, 0, x, y)) {
                put_indexed_pixel(frame, palette, left, top, x, y, color);
            }
        }
    }
}

void put_combined(
    Frame& frame, const PiImage& palette, const CdgSheet& sheet,
    unsigned image, int left, int top
) {
    require_view(
        sheet.layout == CdgSheet::alpha_and_colors,
        "CD2 is not an alpha/color sheet"
    );
    for (unsigned y = 0; y < sheet.height; ++y) {
        for (unsigned x = 0; x < sheet.width; ++x) {
            if (!sheet.bit(image, 0, x, y)) {
                continue;
            }
            unsigned color = 0;
            for (unsigned plane = 0; plane < 4; ++plane) {
                if (sheet.bit(image, plane + 1, x, y)) {
                    color |= (1u << plane);
                }
            }
            put_indexed_pixel(frame, palette, left, top, x, y, color);
        }
    }
}

void put_opaque(
    Frame& frame, const PiImage& palette, const CdgSheet& sheet,
    unsigned image, int left, int top
) {
    require_view(sheet.layout == CdgSheet::colors_only,
                 "CD2 is not an opaque color sheet");
    for (unsigned y = 0; y < sheet.height; ++y) {
        for (unsigned x = 0; x < sheet.width; ++x) {
            unsigned color = 0;
            for (unsigned plane = 0; plane < 4; ++plane) {
                if (sheet.bit(image, plane, x, y)) {
                    color |= (1u << plane);
                }
            }
            put_indexed_pixel(frame, palette, left, top, x, y, color);
        }
    }
}

void fill_rect(
    Frame& frame, const PiImage& palette, int left, int top,
    int width, int height, unsigned color
) {
    for (int y = 0; y < height; ++y) {
        for (int x = 0; x < width; ++x) {
            put_indexed_pixel(frame, palette, left, top, unsigned(x), unsigned(y), color);
        }
    }
}

std::array<std::uint8_t, 7> glyph(char ch) {
    switch (ch) {
    case 'A': return {14, 17, 17, 31, 17, 17, 17};
    case 'B': return {30, 17, 17, 30, 17, 17, 30};
    case 'C': return {14, 17, 16, 16, 16, 17, 14};
    case 'D': return {30, 17, 17, 17, 17, 17, 30};
    case 'E': return {31, 16, 16, 30, 16, 16, 31};
    case 'F': return {31, 16, 16, 30, 16, 16, 16};
    case 'H': return {17, 17, 17, 31, 17, 17, 17};
    case 'I': return {14, 4, 4, 4, 4, 4, 14};
    case 'L': return {16, 16, 16, 16, 16, 16, 31};
    case 'M': return {17, 27, 21, 21, 17, 17, 17};
    case 'N': return {17, 25, 21, 19, 17, 17, 17};
    case 'O': return {14, 17, 17, 17, 17, 17, 14};
    case 'P': return {30, 17, 17, 30, 16, 16, 16};
    case 'R': return {30, 17, 17, 30, 20, 18, 17};
    case 'S': return {15, 16, 16, 14, 1, 1, 30};
    case 'T': return {31, 4, 4, 4, 4, 4, 4};
    case 'U': return {17, 17, 17, 17, 17, 17, 14};
    case 'Y': return {17, 17, 10, 4, 4, 4, 4};
    default: return {0, 0, 0, 0, 0, 0, 0};
    }
}

void put_text(
    Frame& frame, const PiImage& palette, int left, int top,
    const char* text, unsigned color, int scale = 2
) {
    for (const char* p = text; *p; ++p, left += 6 * scale) {
        const auto rows = glyph(*p);
        for (unsigned y = 0; y < rows.size(); ++y) {
            for (unsigned x = 0; x < 5; ++x) {
                if ((rows[y] & (1u << (4 - x))) == 0) continue;
                fill_rect(frame, palette, left + int(x) * scale,
                          top + int(y) * scale, scale, scale, color);
            }
        }
    }
}

void put_shadow(Frame& frame, const PiImage& palette, int left, int top) {
    fill_rect(frame, palette, left + portrait_width, top + raised,
              raised, portrait_height, 1);
    fill_rect(frame, palette, left + raised, top + portrait_height,
              portrait_width, raised, 1);
}

void darken_portrait(
    Frame& frame, const PiImage& palette, int left, int top
) {
    for (int y = 0; y < portrait_height; ++y) {
        for (int x = (y & 1); x < portrait_width; x += 2) {
            put_indexed_pixel(frame, palette, left, top,
                              unsigned(x), unsigned(y), 1);
        }
    }
}

int option_top(unsigned choice) {
    return (choice >= unsigned(menu::OptionChoice::quit))
        ? menu_top + int(menu::OptionChoice::reset) * label_height +
            (int(choice) - int(menu::OptionChoice::reset)) * command_height
        : menu_top + int(choice) * label_height;
}

Frame render_title(
    const PiImage& background, const CdgSheet& labels,
    const CdgSheet& cursors, const menu::State& state
) {
    require_view(
        background.width == 640 && background.height == 400,
        "OP1.PI is not a 640x400 title background"
    );
    require_view(
        labels.width == label_width && labels.height == label_height &&
            labels.image_count >= choice_count,
        "SFT2.CD2 lacks main-menu labels"
    );
    require_view(
        cursors.width == cursor_width && cursors.height == label_height &&
            cursors.image_count >= 2,
        "CAR.CD2 lacks menu cursors"
    );
    require_view(
        state.screen() == menu::Screen::main &&
            state.selection() < choice_count,
        "main-menu selection out of range"
    );

    Frame frame = background_frame(background);
    for (unsigned choice = 0; choice < choice_count; ++choice) {
        const int top = menu_top + int(choice) * command_height;
        const unsigned color = (choice == state.selection()) ? color_active :
            ((choice == unsigned(menu::MainChoice::extra) &&
              !state.extra_unlocked()) ? color_locked : color_inactive);
        put_monochrome(frame, background, labels, choice, command_left, top, color);
    }
    const int top = menu_top + int(state.selection()) * command_height;
    put_combined(frame, background, cursors, 0, cursor_left, top);
    put_combined(frame, background, cursors, 1, cursor_right, top);
    return frame;
}

Frame render_options(
    const PiImage& background, const CdgSheet& numerals,
    const CdgSheet& labels, const CdgSheet& cursors, const menu::State& state
) {
    require_view(
        state.screen() == menu::Screen::options &&
            state.selection() < option_count,
        "option-menu selection out of range"
    );
    require_view(
        numerals.layout == CdgSheet::alpha_only &&
            numerals.width == label_width && numerals.height == label_height &&
            numerals.image_count >= 10,
        "SFT1.CD2 lacks option numerals"
    );
    require_view(labels.image_count >= 24, "SFT2.CD2 lacks option labels");

    Frame frame = background_frame(background);
    const auto& options = state.options();
    for (unsigned choice = 0; choice < option_count; ++choice) {
        const int top = option_top(choice);
        const unsigned color = (choice == state.selection())
            ? color_active : color_inactive;
        switch (menu::OptionChoice(choice)) {
        case menu::OptionChoice::rank:
            put_monochrome(frame, background, labels, 6, option_left, top, color);
            put_monochrome(
                frame, background, labels, 11 + options.rank,
                option_value_left, top, color
            );
            break;
        case menu::OptionChoice::lives:
            put_monochrome(frame, background, labels, 7, option_left, top, color);
            put_monochrome(
                frame, background, numerals, options.lives,
                option_value_left, top, color
            );
            break;
        case menu::OptionChoice::bombs:
            put_monochrome(frame, background, labels, 8, option_left, top, color);
            put_monochrome(
                frame, background, numerals, options.bombs,
                option_value_left, top, color
            );
            break;
        case menu::OptionChoice::bgm: {
            put_monochrome(frame, background, labels, 9, option_left, top, color);
            const unsigned value = (options.bgm_mode == 0)
                ? 18 : 14 + options.bgm_mode;
            put_monochrome(
                frame, background, labels, value, option_value_left, top, color
            );
            break;
        }
        case menu::OptionChoice::sound_effects: {
            put_monochrome(frame, background, labels, 10, option_left, top, color);
            const unsigned value = (options.se_mode == 0)
                ? 18 : 21 - options.se_mode;
            put_monochrome(
                frame, background, labels, value, option_value_left, top, color
            );
            break;
        }
        case menu::OptionChoice::turbo:
            put_monochrome(
                frame, background, labels, options.turbo ? 22 : 23,
                command_left, top, color
            );
            break;
        case menu::OptionChoice::reset:
            put_monochrome(frame, background, labels, 21, command_left, top, color);
            break;
        case menu::OptionChoice::quit:
            put_monochrome(frame, background, labels, 5, command_left, top, color);
            break;
        case menu::OptionChoice::count:
            break;
        }
    }

    const int top = option_top(state.selection());
    const bool two_column = state.selection() < unsigned(menu::OptionChoice::turbo);
    put_combined(
        frame, background, cursors, 0,
        two_column ? option_left : cursor_left, top
    );
    put_combined(
        frame, background, cursors, 1,
        two_column ? option_cursor_right : cursor_right, top
    );
    return frame;
}

Frame render_menu(
    const PiImage& background, const CdgSheet& numerals,
    const CdgSheet& labels, const CdgSheet& cursors, const menu::State& state
) {
    return (state.screen() == menu::Screen::main)
        ? render_title(background, labels, cursors, state)
        : render_options(background, numerals, labels, cursors, state);
}

int portrait_left(application::Playchar playchar) {
    return (playchar == application::Playchar::reimu) ? reimu_left : marisa_left;
}

unsigned portrait_image(application::Playchar playchar) {
    return (playchar == application::Playchar::reimu) ? 0u : 1u;
}

Frame render_character_selection(
    const PiImage& background, const CdgSheet& portraits,
    const selection::State& state
) {
    require_view(background.width == 640 && background.height == 400,
                 "SLB1.PI is not a 640x400 selection background");
    require_view(portraits.width == portrait_width &&
                     portraits.height == portrait_height &&
                     portraits.image_count >= 2,
                 "SL.CD2 lacks character portraits");
    Frame frame = background_frame(background);
    const auto selected = state.playchar();
    const auto other = (selected == application::Playchar::reimu)
        ? application::Playchar::marisa
        : application::Playchar::reimu;
    const int selected_left = portrait_left(selected) - raised;
    const int selected_top = portrait_top - raised;
    put_opaque(frame, background, portraits, portrait_image(selected),
               selected_left, selected_top);
    put_opaque(frame, background, portraits, portrait_image(other),
               portrait_left(other), portrait_top);
    darken_portrait(frame, background, portrait_left(other), portrait_top);
    put_shadow(frame, background, selected_left, selected_top);

    fill_rect(frame, background, 80, 312, 200, 64, 2);
    fill_rect(frame, background, 368, 312, 200, 64, 2);
    put_text(frame, background, 132, 332, "REIMU",
             selected == application::Playchar::reimu ? 15 : 3);
    put_text(frame, background, 414, 332, "MARISA",
             selected == application::Playchar::marisa ? 15 : 3);
    put_text(frame, background, 230, 16, "SELECT PLAYER", 15);
    return frame;
}

Frame render_shot_selection(
    const PiImage& background, const CdgSheet& portraits,
    const selection::State& state
) {
    Frame frame = background_frame(background);
    constexpr int left = 184;
    constexpr int top = 44;
    put_opaque(frame, background, portraits, portrait_image(state.playchar()),
               left, top);
    put_shadow(frame, background, left, top);
    put_text(frame, background, 230, 16, "SELECT SHOT TYPE", 15);

    constexpr int box_left = 320;
    constexpr int box_top = 312;
    constexpr int box_width = 192;
    constexpr int box_height = 24;
    for (unsigned shot = 0; shot < 2; ++shot) {
        const auto shot_type = shot == 0
            ? application::ShotType::a : application::ShotType::b;
        const int top_at = box_top + int(shot) * 24;
        fill_rect(frame, background, box_left + 8, top_at + 8,
                  box_width, box_height, 1);
        fill_rect(frame, background, box_left, top_at,
                  box_width, box_height, 2);
        const unsigned color = !state.available(state.playchar(), shot_type)
            ? color_locked
            : (state.shot_type() == shot_type ? 15 : 3);
        put_text(frame, background, box_left + 52, top_at + 5,
                 shot == 0 ? "TYPE A" : "TYPE B", color);
    }
    return frame;
}

Frame render_main_handoff(
    const PiImage& background, const CdgSheet& portraits,
    const application::State& application_state
) {
    Frame frame = background_frame(background);
    const auto playchar = application_state.resident().playchar;
    put_opaque(frame, background, portraits, portrait_image(playchar), 192, 52);
    fill_rect(frame, background, 128, 320, 384, 48, 2);
    put_text(frame, background, 200, 330, "MAIN HANDOFF READY", 15);
    return frame;
}

void write_bmp(const std::string& path, const Frame& frame) {
    const size_t stride = (size_t(frame.width) * 3 + 3) & ~size_t(3);
    require_view(
        stride * frame.height <= UINT32_MAX - 54,
        "title screenshot is too large"
    );
    Bytes bmp(54 + stride * frame.height);
    bmp[0] = 'B';
    bmp[1] = 'M';
    put32(bmp, 2, uint32_t(bmp.size()));
    put32(bmp, 10, 54);
    put32(bmp, 14, 40);
    put32(bmp, 18, frame.width);
    put32(bmp, 22, frame.height);
    put16(bmp, 26, 1);
    put16(bmp, 28, 24);
    put32(bmp, 34, uint32_t(stride * frame.height));
    for (size_t y = 0; y < frame.height; ++y) {
        const size_t row = 54 + (frame.height - y - 1) * stride;
        for (size_t x = 0; x < frame.width; ++x) {
            const uint32_t color = frame.pixels[y * frame.width + x];
            bmp[row + x * 3 + 0] = uint8_t(color);
            bmp[row + x * 3 + 1] = uint8_t(color >> 8);
            bmp[row + x * 3 + 2] = uint8_t(color >> 16);
        }
    }
    std::ofstream output(path, std::ios::binary);
    require_view(bool(output), "cannot open title screenshot");
    output.write(reinterpret_cast<const char*>(bmp.data()), std::streamsize(bmp.size()));
    require_view(bool(output), "cannot write title screenshot");
}

struct MainSprites {
    sprite::Sheet reimu, marisa, items, stage_tiles, enemies;
    Bytes standard;
    PiImage palette;
    stage::TileImages reimu_tiles, marisa_tiles;
    stage::Background background;
    explicit MainSprites(const MainAssets& assets)
        : reimu(assets.reimu), marisa(assets.marisa), items(assets.items), stage_tiles(assets.stage_tiles),
          enemies(assets.enemies), standard(assets.standard),
          reimu_tiles(assets.reimu_map_tiles), marisa_tiles(assets.marisa_map_tiles),
          background(assets.map, assets.standard) {
        require_view(background.required_image_count() <= reimu_tiles.count() &&
                     background.required_image_count() <= marisa_tiles.count(), "MAP references absent MPN tile");
        // Stage 1's sprite load replaces the eyecatch palette before normal
        // rendering. EYE.RGB belongs to the earlier startup transition.
        require_view(stage_tiles.has_palette(), "ST00.BFT must supply the stage palette");
        palette.palette = stage_tiles.palette();
        require_view(reimu.width() == 32 && reimu.height() == 48 && reimu.count() >= 3 &&
                     marisa.width() == 32 && marisa.height() == 48 && marisa.count() >= 3 &&
                     items.width() == 16 && items.height() == 16 && items.count() == 100 &&
                     enemies.width() == 32 && enemies.height() == 32 && enemies.count() == 24,
                     "MAIN sprite resource geometry changed");
    }
};

void put_sprite(Frame& frame, const PiImage& palette, const sprite::Sheet& sheet,
                unsigned image, int left, int top, bool white = false) {
    for (unsigned y = 0; y < sheet.height(); ++y) {
        for (unsigned x = 0; x < sheet.width(); ++x) {
            const auto color = sheet.pixel(image, x, y);
            if (!color) continue;
            put_indexed_pixel(frame, palette, left, top, x, y, white ? 15 : color);
        }
    }
}

Frame render_main(const MainSprites& sprites, const gameplay::State& state,
                  application::Playchar playchar) {
    Frame frame{640, 400, std::vector<std::uint32_t>(640 * 400, 0xff000000u)};
    const auto& tiles = playchar == application::Playchar::reimu ? sprites.reimu_tiles : sprites.marisa_tiles;
    // Full host redraw replaces PC-98 dirty tile/EGC copies. Clip to the
    // original playfield; the scroll ring owns all 400 physical rows.
    for (unsigned y=16; y<384; ++y) {
        for (unsigned x=0; x<384; ++x) {
            const auto image = sprites.background.image_at(x,y);
            put_indexed_pixel(frame,sprites.palette,32,0,x,y,
                tiles.pixel(image,x%16,sprites.background.row_pixel(y)));
        }
    }
    const auto& shots = state.shots().snapshot();
    const auto pixels = [](std::int16_t coordinate) {
        return coordinate >= 0 ? coordinate / 16 : -((-int(coordinate)+15)/16);
    };
    for (const auto& draw:state.enemies().render_sprites()) {
        if (!draw.visible) continue;
        if (draw.pattern>=4 && draw.pattern<28) {
            put_sprite(frame,sprites.palette,sprites.enemies,draw.pattern-4,
                       16+pixels(draw.position.x),pixels(draw.position.y),draw.white);
        } else if (draw.pattern>=128) {
            require_view(unsigned(draw.pattern-128)<sprites.stage_tiles.count(),"enemy references absent stage sprite");
            put_sprite(frame,sprites.palette,sprites.stage_tiles,draw.pattern-128,
                       16+pixels(draw.position.x),pixels(draw.position.y),draw.white);
        } else throw std::runtime_error("enemy references unsupported sprite sheet");
    }
    if (shots.laser.time > 32) {
        const auto dots = shots.laser.dots();
        const auto bottom = shots.laser.bottom.current;
        for (int side : {-24,24}) {
            const int left = 32+pixels(bottom.x)+side-4;
            for (int y=0;y<pixels(bottom.y);++y) for (unsigned x=0;x<8;++x) {
                if (dots & (0x80u >> x)) {
                    put_indexed_pixel(frame,sprites.palette,left,16,x,unsigned(y),8+state.frames()%2);
                }
            }
        }
    }
    // Target shots_render draws the highest slot first, with the laser
    // underneath. Convert global patterns into the original MIKO16 sheet.
    for (unsigned i=shot::pool_size;i-- > 0;) {
        const auto& entity = shots.entities[i];
        if (entity.flag==shot::free || entity.flag>=shot::remove) continue;
        const auto pattern = static_cast<std::uint8_t>(entity.pattern+
            (entity.flag==shot::alive ? entity.age&1u : 0u));
        require_view(pattern>=28 && pattern<128,"shot references absent MIKO16 pattern");
        put_sprite(frame,sprites.palette,sprites.items,pattern-28,
            32+pixels(entity.position.current.x)-8,16+pixels(entity.position.current.y)-8);
    }
    const auto& position = state.player().position();
    const unsigned cel = position.velocity.x < 0 ? 1 : (position.velocity.x > 0 ? 2 : 0);
    const bool white = state.frames() < 64 && state.frames() % 4 == 0;
    put_sprite(frame, sprites.palette,
               playchar == application::Playchar::reimu ? sprites.reimu : sprites.marisa,
               cel, 32 + position.current.x / 16 - 16,
               16 + position.current.y / 16 - 24, white);
    if (shot::level_for_power(state.score().power)>=2) {
        for (int side : {0,48}) {
            put_sprite(frame,sprites.palette,sprites.items,
                playchar==application::Playchar::reimu ? 10 : 11,
                pixels(shots.options.x)+side,16+pixels(shots.options.y)-8);
        }
    }
    for (const auto& point:state.gathers().points()) {
        const int left=28+pixels(point.position.x),top=12+pixels(point.position.y);
        for (unsigned y=0;y<8;++y) for (unsigned x=0;x<8;++x) {
            if (gather::pixel(x,y)) put_indexed_pixel(frame,sprites.palette,left,top,x,y,point.color);
        }
    }
    for (const auto& entity:state.sparks().snapshot().entities) {
        if (entity.flag!=1) continue;
        const int left=28+pixels(entity.center.current.x),top=12+pixels(entity.center.current.y);
        for (unsigned y=0;y<8;++y) for (unsigned x=0;x<8;++x) {
            if (spark::pixel(entity.age&7u,x,y)) put_indexed_pixel(frame,sprites.palette,left,top,x,y,12);
        }
    }
    for (const auto& entity : state.items().entities()) {
        if (entity.flag != th04::portable::item::Flag::alive) continue;
        const auto point = entity.position.current;
        const int x = point.x >= 0 ? point.x / 16 : -((-int(point.x) + 15) / 16);
        const int y = point.y >= 0 ? point.y / 16 : -((-int(point.y) + 15) / 16);
        // 3 player + 1 death + 24 MIKO32 patterns put MIKO16 at global
        // slot 28. IT_POWER is global slot 44, hence local index 16.
        put_sprite(frame, sprites.palette, sprites.items,
                   16u + static_cast<unsigned>(entity.type), 32 + x - 8, 16 + y - 8);
    }
    // Original foreground order puts enemy bullets after player and items.
    const auto& bullets=state.bullets().snapshot();
    for (unsigned index=bullet::pool_size;index;) {
        --index;const auto& b=bullets.entities[index];if (b.flag!=1) continue;
        const auto p=b.position.current;
        if (index<bullet::pellet_count && !bullets.clear_time && !bullets.zap_frame) {
            if (!bullets.pellet_visible[index]) continue;
            const int left=28+pixels(p.x),top=12+pixels(p.y);
            // The white top is an eight-pixel disk; the purple lower pass
            // repeats its first row at Y+3, overlapping the six white rows
            // and producing eight output rows without a bitmap array.
            for (unsigned y=0;y<8;++y) for (unsigned x=0;x<8;++x) {
                const auto color=bullet::pellet_pixel(x,y);
                if (color) put_indexed_pixel(frame,sprites.palette,left,top,x,y,color);
            }
        } else if (index<bullet::pellet_count || b.phase<=bullet::Phase::cloud_backward) {
            require_view(b.pattern>=28 && unsigned(b.pattern-28)<sprites.items.count(),"bullet references absent 16px sprite");
            put_sprite(frame,sprites.palette,sprites.items,b.pattern-28,24+pixels(p.x),8+pixels(p.y));
        } else if (p.x>=0 && p.x<6144 && p.y>=0 && p.y<5888) {
            const bool blue=b.pattern==54 || b.pattern==55 || b.pattern==57 || (b.pattern>=76 && b.pattern<92);
            const unsigned pattern=(blue ? 19 : 23)+unsigned(b.phase)/4;
            put_sprite(frame,sprites.palette,sprites.enemies,pattern-4,16+pixels(p.x),pixels(p.y));
        }
    }
    return frame;
}

class FrontEnd {
public:
    FrontEnd(
        const PiImage& title_background, const CdgSheet& numerals,
        const CdgSheet& labels, const CdgSheet& cursors,
        const PiImage& selection_background, const CdgSheet& portraits,
        const MainAssets* main_assets = nullptr
    ) : title_background_(title_background), numerals_(numerals), labels_(labels),
        cursors_(cursors), selection_background_(selection_background),
        portraits_(portraits), frame_(render()) {
        if (main_assets && !main_assets->reimu.empty()) {
            sprites_ = std::make_unique<MainSprites>(*main_assets);
        }
    }

    const Frame& frame() const { return frame_; }
    bool live_main() const { return screen_ == Screen::main_handoff && bool(main_); }
    unsigned slowdown() const { return main_ ? main_->bullets().snapshot().slowdown : 1; }
    void advance(std::uint16_t held_input, bool shift) {
        if (live_main()) {
            main_->update(held_input, shift, false, sprites_->background.last_delta());
            sprites_->background.update();
            frame_ = render();
        }
        else if (screen_ == Screen::menu) application_.advance_op_menu_frame();
    }
    gameplay::State& main_state() {
        require_view(bool(main_), "MAIN scene is not active");
        return *main_;
    }

    bool input(menu::Input pressed) {
        bool close = false;
        switch (screen_) {
        case Screen::menu: {
            const menu::Result result = menu_.handle(pressed);
            if (result.kind == menu::ResultKind::quit) {
                application_.exit_from_op();
                close = true;
            } else if (result.kind == menu::ResultKind::choose_main) {
                if (result.choice == menu::MainChoice::game ||
                    result.choice == menu::MainChoice::extra) {
                    extra_ = result.choice == menu::MainChoice::extra;
                    selection_ = selection::State{};
                    screen_ = Screen::selection;
                } else {
                    std::cout << "title selection=" << unsigned(result.choice)
                              << " (not ported yet)" << std::endl;
                }
            }
            break;
        }
        case Screen::selection: {
            const selection::Result result = selection_.handle(pressed);
            if (result.kind == selection::ResultKind::canceled) {
                screen_ = Screen::menu;
            } else if (result.kind == selection::ResultKind::chosen) {
                application_.apply_options(menu_.options());
                if (extra_) {
                    application_.start_extra(result.playchar, result.shot_type);
                } else {
                    application_.start_normal(result.playchar, result.shot_type);
                }
                screen_ = Screen::main_handoff;
                if (sprites_) {
                    main_ = std::make_unique<gameplay::State>(application_);
                    main_->load_stage(sprites_->standard);
                }
                std::cout << "MAIN handoff playchar="
                          << unsigned(result.playchar)
                          << " shot=" << unsigned(result.shot_type)
                          << " generation=" << application_.generation()
                          << std::endl;
            }
            break;
        }
        case Screen::main_handoff:
            if (pressed == menu::Input::cancel) {
                close = true;
            }
            break;
        }
        frame_ = render();
        return close;
    }

private:
    enum class Screen { menu, selection, main_handoff };

    Frame render() const {
        switch (screen_) {
        case Screen::menu:
            return render_menu(
                title_background_, numerals_, labels_, cursors_, menu_
            );
        case Screen::selection:
            return (selection_.screen() == selection::Screen::playchar)
                ? render_character_selection(
                    selection_background_, portraits_, selection_
                )
                : render_shot_selection(
                    selection_background_, portraits_, selection_
                );
        case Screen::main_handoff:
            if (main_) return render_main(*sprites_, *main_, application_.resident().playchar);
            return render_main_handoff(
                selection_background_, portraits_, application_
            );
        }
        throw std::logic_error("invalid portable front-end screen");
    }

    const PiImage& title_background_;
    const CdgSheet& numerals_;
    const CdgSheet& labels_;
    const CdgSheet& cursors_;
    const PiImage& selection_background_;
    const CdgSheet& portraits_;
    menu::State menu_;
    selection::State selection_;
    application::State application_;
    Screen screen_ = Screen::menu;
    bool extra_ = false;
    std::unique_ptr<MainSprites> sprites_;
    std::unique_ptr<gameplay::State> main_;
    Frame frame_;
};

#ifdef _WIN32

struct Win32Title {
    FrontEnd front_end;
    Clock::time_point next_tick = Clock::now() + frame_period;

    Win32Title(
        const PiImage& background_, const CdgSheet& numerals_,
        const CdgSheet& labels_, const CdgSheet& cursors_,
        const PiImage& selection_background_, const CdgSheet& portraits_,
        const MainAssets& main_assets
    ) : front_end(background_, numerals_, labels_, cursors_,
                  selection_background_, portraits_, &main_assets) {}

    bool input(menu::Input pressed) {
        return front_end.input(pressed);
    }
};

LRESULT CALLBACK title_window_proc(
    HWND window, UINT message, WPARAM wparam, LPARAM lparam
) {
    Win32Title* title = reinterpret_cast<Win32Title*>(
        GetWindowLongPtrW(window, GWLP_USERDATA)
    );
    if (message == WM_NCCREATE) {
        const auto* create = reinterpret_cast<const CREATESTRUCTW*>(lparam);
        title = static_cast<Win32Title*>(create->lpCreateParams);
        SetWindowLongPtrW(window, GWLP_USERDATA, reinterpret_cast<LONG_PTR>(title));
    }
    switch (message) {
    case WM_TIMER:
        if (title) {
            const auto now = Clock::now();
            unsigned ticks = 0;
            while (now >= title->next_tick && ticks < 4) {
                std::uint16_t held = 0;
                const bool active = GetForegroundWindow() == window;
                if (active && GetAsyncKeyState(VK_UP) & 0x8000) held |= player::up;
                if (active && GetAsyncKeyState(VK_DOWN) & 0x8000) held |= player::down;
                if (active && GetAsyncKeyState(VK_LEFT) & 0x8000) held |= player::left;
                if (active && GetAsyncKeyState(VK_RIGHT) & 0x8000) held |= player::right;
                if (active && GetAsyncKeyState('Z') & 0x8000) held |= shot::input_shot;
                title->front_end.advance(held, active && (GetAsyncKeyState(VK_SHIFT) & 0x8000));
                title->next_tick += frame_period*title->front_end.slowdown();
                ++ticks;
            }
            if (ticks == 4 && now >= title->next_tick) title->next_tick = now + frame_period;
            if (ticks && title->front_end.live_main()) InvalidateRect(window, nullptr, FALSE);
            return 0;
        }
        break;
    case WM_KEYDOWN: {
        if (!title) break;
        if (lparam & (LPARAM(1) << 30)) return 0;
        bool handled = true;
        bool close = false;
        if (wparam == VK_UP) title->input(menu::Input::up);
        else if (wparam == VK_DOWN) title->input(menu::Input::down);
        else if (wparam == VK_LEFT) title->input(menu::Input::left);
        else if (wparam == VK_RIGHT) title->input(menu::Input::right);
        else if (wparam == VK_RETURN || wparam == 'Z') close = title->input(menu::Input::confirm);
        else if (wparam == VK_ESCAPE) close = title->input(menu::Input::cancel);
        else handled = false;
        if (!handled) break;
        if (close) {
            DestroyWindow(window);
            return 0;
        }
        InvalidateRect(window, nullptr, FALSE);
        return 0;
    }
    case WM_PAINT:
        if (title) {
            PAINTSTRUCT paint{};
            HDC dc = BeginPaint(window, &paint);
            RECT client{};
            GetClientRect(window, &client);
            BITMAPINFO info{};
            info.bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
            const Frame& frame = title->front_end.frame();
            info.bmiHeader.biWidth = LONG(frame.width);
            info.bmiHeader.biHeight = -LONG(frame.height);
            info.bmiHeader.biPlanes = 1;
            info.bmiHeader.biBitCount = 32;
            info.bmiHeader.biCompression = BI_RGB;
            SetStretchBltMode(dc, COLORONCOLOR);
            StretchDIBits(
                dc, 0, 0, client.right, client.bottom,
                0, 0, int(frame.width), int(frame.height),
                frame.pixels.data(), &info, DIB_RGB_COLORS, SRCCOPY
            );
            EndPaint(window, &paint);
            return 0;
        }
        break;
    case WM_DESTROY:
        PostQuitMessage(0);
        return 0;
    }
    return DefWindowProcW(window, message, wparam, lparam);
}

void show_window(
    const PiImage& background, const CdgSheet& numerals,
    const CdgSheet& labels, const CdgSheet& cursors,
    const PiImage& selection_background, const CdgSheet& portraits,
    const MainAssets& main_assets
) {
    Win32Title title(
        background, numerals, labels, cursors, selection_background, portraits, main_assets
    );
    const HINSTANCE instance = GetModuleHandleW(nullptr);
    const wchar_t class_name[] = L"TH04Port64Title";
    WNDCLASSW window_class{};
    window_class.lpfnWndProc = title_window_proc;
    window_class.hInstance = instance;
    window_class.hCursor = LoadCursorW(nullptr, MAKEINTRESOURCEW(32512));
    window_class.lpszClassName = class_name;
    require_view(
        RegisterClassW(&window_class) || GetLastError() == ERROR_CLASS_ALREADY_EXISTS,
        "cannot register Win32 title class"
    );
    RECT rectangle{0, 0, 1280, 800};
    AdjustWindowRect(&rectangle, WS_OVERLAPPEDWINDOW, FALSE);
    HWND window = CreateWindowExW(
        0, class_name, L"TH04 native x64 title bring-up",
        WS_OVERLAPPEDWINDOW | WS_VISIBLE, CW_USEDEFAULT, CW_USEDEFAULT,
        rectangle.right - rectangle.left, rectangle.bottom - rectangle.top,
        nullptr, nullptr, instance, &title
    );
    require_view(window != nullptr, "cannot create Win32 title window");
    require_view(SetTimer(window, 1, 4, nullptr) != 0, "cannot create MAIN frame timer");
    MSG message{};
    while (GetMessageW(&message, nullptr, 0, 0) > 0) {
        TranslateMessage(&message);
        DispatchMessageW(&message);
    }
}

#else

void show_window(
    const PiImage& background, const CdgSheet& numerals,
    const CdgSheet& labels, const CdgSheet& cursors,
    const PiImage& selection_background, const CdgSheet& portraits,
    const MainAssets& main_assets
) {
    require_view(SDL_Init(SDL_INIT_VIDEO | SDL_INIT_EVENTS) == 0, SDL_GetError());
    struct SdlQuit { ~SdlQuit() { SDL_Quit(); } } quit;
    SDL_Window* window = SDL_CreateWindow(
        "TH04 native x64 title bring-up", SDL_WINDOWPOS_CENTERED,
        SDL_WINDOWPOS_CENTERED, 1280, 800, SDL_WINDOW_RESIZABLE
    );
    require_view(window != nullptr, SDL_GetError());
    struct WindowOwner {
        SDL_Window* value;
        ~WindowOwner() { SDL_DestroyWindow(value); }
    } window_owner{window};
    SDL_Renderer* renderer = SDL_CreateRenderer(
        window, -1, SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC
    );
    if (!renderer) {
        renderer = SDL_CreateRenderer(window, -1, SDL_RENDERER_SOFTWARE);
    }
    require_view(renderer != nullptr, SDL_GetError());
    struct RendererOwner {
        SDL_Renderer* value;
        ~RendererOwner() { SDL_DestroyRenderer(value); }
    } renderer_owner{renderer};
    SDL_Texture* texture = SDL_CreateTexture(
        renderer, SDL_PIXELFORMAT_ARGB8888, SDL_TEXTUREACCESS_STREAMING,
        int(background.width), int(background.height)
    );
    require_view(texture != nullptr, SDL_GetError());
    struct TextureOwner {
        SDL_Texture* value;
        ~TextureOwner() { SDL_DestroyTexture(value); }
    } texture_owner{texture};

    FrontEnd front_end(
        background, numerals, labels, cursors, selection_background, portraits, &main_assets
    );
    auto next_tick = Clock::now() + frame_period;
    bool running = true;
    bool dirty = true;
    Frame frame;
    while (running) {
        SDL_Event event{};
        // Process the waited event in place. Pushing it back would move it
        // behind later key events and could invert rapid menu confirmations.
        for (bool available = SDL_PollEvent(&event) ||
                 (!dirty && SDL_WaitEventTimeout(&event, 4));
             available; available = SDL_PollEvent(&event)) {
            if (event.type == SDL_QUIT) running = false;
            if (event.type != SDL_KEYDOWN || event.key.repeat) continue;
            switch (event.key.keysym.sym) {
            case SDLK_UP:
                front_end.input(menu::Input::up);
                dirty = true;
                break;
            case SDLK_DOWN:
                front_end.input(menu::Input::down);
                dirty = true;
                break;
            case SDLK_LEFT:
                front_end.input(menu::Input::left);
                dirty = true;
                break;
            case SDLK_RIGHT:
                front_end.input(menu::Input::right);
                dirty = true;
                break;
            case SDLK_RETURN:
            case SDLK_KP_ENTER:
            case SDLK_z:
                if (front_end.input(menu::Input::confirm)) running = false;
                dirty = true;
                break;
            case SDLK_ESCAPE:
                if (front_end.input(menu::Input::cancel)) running = false;
                dirty = true;
                break;
            default:
                break;
            }
        }
        if (!running) break;
        const auto now = Clock::now();
        unsigned ticks = 0;
        while (now >= next_tick && ticks < 4) {
            const auto* keys = SDL_GetKeyboardState(nullptr);
            std::uint16_t held = 0;
            if (SDL_GetWindowFlags(window) & SDL_WINDOW_INPUT_FOCUS) {
                if (keys[SDL_SCANCODE_UP]) held |= player::up;
                if (keys[SDL_SCANCODE_DOWN]) held |= player::down;
                if (keys[SDL_SCANCODE_LEFT]) held |= player::left;
                if (keys[SDL_SCANCODE_RIGHT]) held |= player::right;
                if (keys[SDL_SCANCODE_Z]) held |= shot::input_shot;
            }
            const bool focused = (SDL_GetWindowFlags(window) & SDL_WINDOW_INPUT_FOCUS) != 0;
            front_end.advance(held, focused && (keys[SDL_SCANCODE_LSHIFT] || keys[SDL_SCANCODE_RSHIFT]));
            dirty |= front_end.live_main();
            next_tick += frame_period*front_end.slowdown();
            ++ticks;
        }
        if (ticks == 4 && now >= next_tick) next_tick = now + frame_period;
        if (dirty) {
            frame = front_end.frame();
            SDL_UpdateTexture(
                texture, nullptr, frame.pixels.data(), int(frame.width * 4)
            );
            dirty = false;
        }
        int output_width = 0;
        int output_height = 0;
        SDL_GetRendererOutputSize(renderer, &output_width, &output_height);
        const double scale = std::min(
            double(output_width) / frame.width,
            double(output_height) / frame.height
        );
        SDL_Rect destination{
            int((output_width - frame.width * scale) / 2),
            int((output_height - frame.height * scale) / 2),
            int(frame.width * scale), int(frame.height * scale)
        };
        SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255);
        SDL_RenderClear(renderer);
        SDL_RenderCopy(renderer, texture, nullptr, &destination);
        SDL_RenderPresent(renderer);
    }
}

#endif

} // namespace

void run_title(
    const PiImage& background, const Bytes& numeral_bytes,
    const Bytes& label_bytes, const Bytes& cursor_bytes,
    const PiImage& selection_background, const Bytes& portrait_bytes,
    const MainAssets& main_assets,
    const std::string& screenshot, const std::string& options_screenshot,
    const std::string& character_screenshot,
    const std::string& shot_screenshot,
    const std::string& handoff_screenshot,
    const std::string& main_screenshot, const std::string& shooting_screenshots,
    const std::string& combat_screenshots, bool window
) {
    const CdgSheet numerals(numeral_bytes);
    const CdgSheet labels(label_bytes);
    const CdgSheet cursors(cursor_bytes);
    const CdgSheet portraits(portrait_bytes);
    menu::State initial_state;
    const Frame initial = render_menu(
        background, numerals, labels, cursors, initial_state
    );
    if (!screenshot.empty()) {
        write_bmp(screenshot, initial);
        std::cout << "title 640x400 screenshot=" << screenshot << std::endl;
    }
    if (!options_screenshot.empty()) {
        menu::State options_state;
        options_state.handle(menu::Input::down);
        options_state.handle(menu::Input::down);
        options_state.handle(menu::Input::down);
        options_state.handle(menu::Input::confirm);
        write_bmp(
            options_screenshot,
            render_menu(background, numerals, labels, cursors, options_state)
        );
        std::cout << "options 640x400 screenshot=" << options_screenshot
                  << std::endl;
    }
    if (!character_screenshot.empty() || !shot_screenshot.empty()) {
        selection::State selection_state;
        if (!character_screenshot.empty()) {
            write_bmp(
                character_screenshot,
                render_character_selection(
                    selection_background, portraits, selection_state
                )
            );
            std::cout << "character selection 640x400 screenshot="
                      << character_screenshot << std::endl;
        }
        if (!shot_screenshot.empty()) {
            selection_state.handle(menu::Input::confirm);
            write_bmp(
                shot_screenshot,
                render_shot_selection(
                    selection_background, portraits, selection_state
                )
            );
            std::cout << "shot selection 640x400 screenshot="
                      << shot_screenshot << std::endl;
        }
    }
    if (!handoff_screenshot.empty()) {
        FrontEnd front_end(
            background, numerals, labels, cursors,
            selection_background, portraits
        );
        front_end.input(menu::Input::confirm);
        front_end.input(menu::Input::confirm);
        front_end.input(menu::Input::confirm);
        write_bmp(handoff_screenshot, front_end.frame());
        std::cout << "MAIN handoff 640x400 screenshot="
                  << handoff_screenshot << std::endl;
    }
    if (!main_screenshot.empty()) {
        FrontEnd front_end(background, numerals, labels, cursors,
                           selection_background, portraits, &main_assets);
        front_end.input(menu::Input::confirm);
        front_end.input(menu::Input::confirm);
        front_end.input(menu::Input::confirm);
        // Only this explicitly requested inspection fixture injects items.
        // Interactive MAIN has no substitute enemy or drop schedule.
        for (unsigned i = 0; i < 7; ++i) {
            front_end.main_state().add_item(
                {static_cast<std::int16_t>((64 + i * 40) * 16), 160 * 16},
                static_cast<th04::portable::item::Type>(i)
            );
        }
        for (unsigned frame = 0; frame < 60; ++frame) {
            front_end.advance(player::right | player::up, frame >= 30);
        }
        write_bmp(main_screenshot, front_end.frame());
        const auto& position = front_end.main_state().player().position().current;
        std::cout << "MAIN scene frames=60 player=" << position.x << ',' << position.y
                  << " screenshot=" << main_screenshot << std::endl;
    }
    if (!shooting_screenshots.empty()) {
        for (unsigned character=0;character<2;++character) for (unsigned type=0;type<2;++type) {
            FrontEnd front_end(background,numerals,labels,cursors,
                               selection_background,portraits,&main_assets);
            front_end.input(menu::Input::confirm);
            if (character) front_end.input(menu::Input::right);
            front_end.input(menu::Input::confirm);
            if (type) front_end.input(menu::Input::down);
            front_end.input(menu::Input::confirm);
            // Explicit inspection fixture: collect an actual full-power
            // item, then fire. Ordinary gameplay does not inject this item.
            front_end.main_state().add_item(front_end.main_state().player().position().current,
                                           th04::portable::item::Type::full_power);
            front_end.advance(0,false);
            for (unsigned frame=0;frame<66;++frame) front_end.advance(shot::input_shot,false);
            const auto path = shooting_screenshots+"/"+
                (std::string(character ? "marisa-" : "reimu-")+(type ? "b.bmp" : "a.bmp"));
            write_bmp(path,front_end.frame());
            std::cout << "MAIN shooting power=" << +front_end.main_state().score().power
                      << " screenshot=" << path << '\n';
        }
    }
    if (!combat_screenshots.empty()) {
        for (unsigned character=0;character<2;++character) {
            FrontEnd front_end(background,numerals,labels,cursors,
                               selection_background,portraits,&main_assets);
            front_end.input(menu::Input::confirm);
            if (character) front_end.input(menu::Input::right);
            front_end.input(menu::Input::confirm);
            front_end.input(menu::Input::confirm);
            // Original Stage 1 waves and normal initial power; no injected
            // enemies, pickups or score. Exercise the complete native chain.
            for (unsigned frame=0;frame<1200;++frame) front_end.advance(shot::input_shot,false);
            const auto& state=front_end.main_state();
            const auto path=combat_screenshots+"/"+(character ? "marisa.bmp" : "reimu.bmp");
            write_bmp(path,front_end.frame());
            require_view(state.enemies().snapshot().killed_count>0,"combat fixture killed no enemies");
            std::cout << "MAIN combat frames=1200 killed=" << state.enemies().snapshot().killed_count
                      << " score=" << state.score().score_delta << " power=" << +state.score().power
                      << " screenshot=" << path << '\n';
            FrontEnd barrage(background,numerals,labels,cursors,
                             selection_background,portraits,&main_assets);
            for (unsigned i=0;i<3;++i) barrage.input(menu::Input::down);
            barrage.input(menu::Input::confirm);
            barrage.input(menu::Input::right);barrage.input(menu::Input::right);
            barrage.input(menu::Input::cancel);
            for (unsigned i=0;i<3;++i) barrage.input(menu::Input::up);
            barrage.input(menu::Input::confirm);
            if (character) barrage.input(menu::Input::right);
            barrage.input(menu::Input::confirm);barrage.input(menu::Input::confirm);
            // Select Lunatic through OP, then let real enemies fire. No
            // shooting or injected entities suppresses this barrage fixture.
            for (unsigned frame=0;frame<900;++frame) barrage.advance(0,false);
            unsigned alive=0;
            for (const auto& b:barrage.main_state().bullets().snapshot().entities) alive+=b.flag==1;
            require_view(alive>0,"Lunatic STD fixture produced no bullets");
            const auto bullet_path=combat_screenshots+"/"+(character ? "marisa-bullets.bmp" : "reimu-bullets.bmp");
            write_bmp(bullet_path,barrage.frame());
            std::cout << "MAIN barrage rank=Lunatic frames=900 bullets=" << alive
                      << " screenshot=" << bullet_path << '\n';
        }
    }
    if (window) {
        show_window(
            background, numerals, labels, cursors,
            selection_background, portraits, main_assets
        );
    }
}

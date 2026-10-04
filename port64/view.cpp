#include "view.hpp"
#include "application_state.hpp"
#include "menu_state.hpp"
#include "selection_state.hpp"
#include "main_state.hpp"
#include "stage4.hpp"
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
namespace orange = th04::portable::orange;
namespace circle = th04::portable::circle;
namespace dialog = th04::portable::dialog;

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
    // Kept for partial-plane sprite writes; RGB cannot recover duplicate colors.
    Bytes indices;
    Frame()=default;
    Frame(unsigned w,unsigned h,std::vector<uint32_t> p):width(w),height(h),pixels(std::move(p)) {}
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
        const auto at=size_t(screen_y)*frame.width+screen_x;
        frame.pixels[at]=palette_color(palette,color);
        if(!frame.indices.empty()) frame.indices[at]=static_cast<std::uint8_t>(color);
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

// Heap-owned stage resources keep CDG references and sprite-slot pointers
// stable. Validate a complete candidate before changing MAIN's live actors.
struct StageSprites {
    StageAssets assets;
    sprite::Sheet stage,boss;
    CdgSheet backdrop,faces;
    stage::TileImages tiles;
    stage::Background background;
    th04::portable::stage4::CarpetState carpet;
    StageSprites(const StageSprites&)=delete;
    StageSprites& operator=(const StageSprites&)=delete;
    explicit StageSprites(const StageAssets& source,unsigned resource_stage=1):assets(source),stage(assets.stage_tiles),boss(assets.boss_tiles),
        backdrop(assets.backdrop),faces(assets.boss_faces),tiles(assets.map_tiles),background(assets.map,assets.standard) {
        require_view(stage.count()==(resource_stage==1 ? 18u : (resource_stage==2 ? 16u : 28u)) && stage.width()==32 && stage.height()==32 &&
                     boss.count()==(resource_stage==1 ? 16u : (resource_stage==2 ? 4u : 8u)) && boss.width()==64 && boss.height()==64 && boss.has_palette(),
                     "stage BFNT append contract changed");
        require_view(tiles.count()==(resource_stage==1 ? 75u : (resource_stage==2 ? 84u : 89u)) && background.required_image_count()<=tiles.count(),"stage MAP references absent MPN tile");
        require_view(backdrop.width==(resource_stage==3 ? 256u : 384u) && backdrop.height==(resource_stage==3 ? 256u : 112u) && backdrop.image_count==1 &&
                     backdrop.layout==CdgSheet::colors_only && assets.transition.size()==2048 &&
                     faces.width==128 && faces.height==128 && (faces.image_count==4 || (resource_stage==3 && faces.image_count==3)) && faces.layout==CdgSheet::alpha_and_colors,
                     "Stage2 backdrop/portrait contract changed");
        require_view(!assets.dialog_scripts[0].empty() && !assets.dialog_scripts[1].empty(),"Stage2 dialog script missing");
    }
};

struct MainSprites {
    sprite::Sheet reimu, marisa, items, stage_tiles, boss_tiles, enemies,explosion;
    Bytes backdrop_bytes,transition;
    CdgSheet backdrop;
    std::array<Bytes,2> scripts,face_bytes;
    Bytes boss_face_bytes,gaiji;
    CdgSheet reimu_faces,marisa_faces,boss_faces;
    dialog::Font font;
    std::map<std::string,Bytes> dialog_files;
    struct Slot { const sprite::Sheet* sheet=nullptr;unsigned image=0; };
    std::array<Slot,256> stage_slots{};
    std::vector<std::unique_ptr<sprite::Sheet>> loaded_sheets;
    unsigned stage_end=152;
    Bytes standard;
    std::unique_ptr<StageSprites> second;
    PiImage palette;
    stage::TileImages reimu_tiles, marisa_tiles;
    stage::Background background;
    explicit MainSprites(const MainAssets& assets)
        : reimu(assets.reimu), marisa(assets.marisa), items(assets.items), stage_tiles(assets.stage_tiles),
          boss_tiles(assets.boss_tiles),enemies(assets.enemies),explosion(assets.explosion_sprite),
          backdrop_bytes(assets.orange_background),transition(assets.orange_transition),backdrop(backdrop_bytes),
          scripts(assets.dialog_scripts),face_bytes(assets.player_faces),boss_face_bytes(assets.boss_faces),gaiji(assets.gaiji),
          reimu_faces(face_bytes[0]),marisa_faces(face_bytes[1]),boss_faces(boss_face_bytes),font(assets.font_bitmap),dialog_files(assets.dialog_sprites),standard(assets.standard),
          reimu_tiles(assets.reimu_map_tiles), marisa_tiles(assets.marisa_map_tiles),
          background(assets.map, assets.standard) {
        require_view(background.required_image_count() <= reimu_tiles.count() &&
                     background.required_image_count() <= marisa_tiles.count(), "MAP references absent MPN tile");
        // stage1_setup appends ST00.BMT after the 12 ST00.BFT slots, installs
        // its palette, then sets color zero's red/green components to FF.
        // The two sheets have different widths (32 and 64 pixels).
        require_view(stage_tiles.count()==12 && boss_tiles.count()==12 &&
                     boss_tiles.width()==64 && boss_tiles.height()==32 && boss_tiles.has_palette(),
                     "Stage 1 BFNT append contract changed");
        palette.palette = boss_tiles.palette();
        palette.palette[0]=255;palette.palette[1]=255;
        for(unsigned i=0;i<12;++i) { stage_slots[128+i]={&stage_tiles,i};stage_slots[140+i]={&boss_tiles,i}; }
        require_view(explosion.width()==48 && explosion.height()==48 && explosion.count()==1 &&
                     backdrop.width==384 && backdrop.height==128 && backdrop.image_count==1 &&
                     backdrop.layout==CdgSheet::colors_only && transition.size()==2048,
                     "Orange resource geometry changed");
        require_view(reimu.width() == 32 && reimu.height() == 48 && reimu.count() >= 3 &&
                     marisa.width() == 32 && marisa.height() == 48 && marisa.count() >= 3 &&
                     items.width() == 16 && items.height() == 16 && items.count() == 100 &&
                     enemies.width() == 32 && enemies.height() == 32 && enemies.count() == 24,
                     "MAIN sprite resource geometry changed");
    }
    void install_stage(std::unique_ptr<StageSprites> next) {
        clean_stage(); // Clears every stage slot and first-stage dialog sheets.
        palette.palette=next->boss.palette(); // Later stages have no Stage1 color-zero override.
        background=std::move(next->background);
        second=std::move(next);
        for(unsigned i=0;i<second->stage.count();++i) stage_slots[stage_end++]={&second->stage,i};
        for(unsigned i=0;i<second->boss.count();++i) stage_slots[stage_end++]={&second->boss,i};
    }
    const CdgSheet& boss_portraits() const { return second ? second->faces : boss_faces; }
    void clean_stage() { for(unsigned i=128;i<256;++i) stage_slots[i]={};loaded_sheets.clear();stage_end=128; }
    void load_dialog_sprites(std::string name) {
        for(auto& c:name) if(c>='a' && c<='z') c=static_cast<char>(c-'a'+'A');
        const auto it=dialog_files.find(name);require_view(it!=dialog_files.end(),"dialog references absent sprite file");
        auto sheet=std::make_unique<sprite::Sheet>(it->second);
        require_view(sheet->count()<=256-stage_end,"dialog sprite bank overflow");
        for(unsigned i=0;i<sheet->count();++i) stage_slots[stage_end++]={sheet.get(),i};
        if(sheet->has_palette()) palette.palette=sheet->palette();
        loaded_sheets.push_back(std::move(sheet));
    }
    void diagnostic_boss_sprites() { clean_stage();load_dialog_sprites("ST00.BB1");load_dialog_sprites("ST00.BB2"); }
};

void put_sprite(Frame& frame, const PiImage& palette, const sprite::Sheet& sheet,
                unsigned image, int left, int top, bool white = false,unsigned scale=1) {
    for (unsigned y = 0; y < sheet.height(); ++y) {
        for (unsigned x = 0; x < sheet.width(); ++x) {
            const auto color = sheet.pixel(image, x, y);
            if (!color) continue;
            for (unsigned dy=0;dy<scale;++dy) for (unsigned dx=0;dx<scale;++dx)
                put_indexed_pixel(frame, palette, left, top, x*scale+dx, y*scale+dy, white ? 15 : color);
        }
    }
}

void put_reimu_sprite(Frame& frame,const PiImage& palette,const sprite::Sheet& sheet,
                      unsigned image,int left,int top,orange::DrawKind kind) {
    require_view(!frame.indices.empty(),"Reimu sprite requires palette indices");
    th04::portable::reimu::raster_sprite(sheet,image,left,top,kind,
        [&](int x,int y) { return frame.indices[unsigned(y)*frame.width+unsigned(x)]; },
        [&](int x,int y,std::uint8_t color) { put_indexed_pixel(frame,palette,x,y,0,0,color); });
}

Frame render_main(const MainSprites& sprites, const gameplay::State& state,
                  application::Playchar playchar,std::optional<int> displayed_tone={}) {
    Frame frame{640, 400, std::vector<std::uint32_t>(640 * 400, 0xff000000u)};
    const bool npc_active=state.reimu_active() || state.marisa_active();
    if(npc_active) frame.indices.assign(640*400,0);
    PiImage palette=sprites.palette;
    if (state.boss_active()) {
        const auto& boss=state.boss_snapshot();
        for (unsigned i=0;i<3;++i) palette.palette[i]=boss.palette_zero[i];
        const int tone=std::clamp(displayed_tone.value_or(boss.palette_tone),0,200);
        for (auto& component:palette.palette) {
            const int base=component>>4;
            const int nibble=tone<=100 ? base*tone/100 : 15-(15-base)*(200-tone)/100;
            component=static_cast<std::uint8_t>(nibble*16);
        }
    }
    const auto background_phase=state.orange_background_phase();
    const auto npc_background=th04::portable::reimu::backdrop(background_phase,state.orange_background_frame());
    const bool npc_picture=npc_active && (npc_background.kind==th04::portable::reimu::BackdropKind::picture || npc_background.kind==th04::portable::reimu::BackdropKind::picture_and_mask);
    const bool backdrop=npc_picture || (!npc_active && state.boss_active() && background_phase>=(state.elly_active() ? 2 : 1) && background_phase<254);
    if (backdrop) {
        if(npc_active) {
            require_view(bool(sprites.second),"NPC backdrop has no Stage4 owner");
            fill_rect(frame,palette,32,16,384,56,1);fill_rect(frame,palette,32,328,384,56,1);
            fill_rect(frame,palette,32,72,64,256,1);fill_rect(frame,palette,352,72,64,256,1);
            put_opaque(frame,palette,sprites.second->backdrop,0,96,72);
        } else if(state.elly_active()) {
            require_view(bool(sprites.second),"Elly backdrop has no Stage3 owner");
            fill_rect(frame,palette,32,128,384,256,0);
            put_opaque(frame,palette,sprites.second->backdrop,0,32,16);
        } else if(state.kurumi_active()) {
            require_view(bool(sprites.second),"Kurumi backdrop has no Stage2 owner");
            fill_rect(frame,palette,32,16,384,80,0);
            fill_rect(frame,palette,32,208,384,192,0);
            put_opaque(frame,palette,sprites.second->backdrop,0,32,96);
        } else {
            fill_rect(frame,palette,32,16,384,120,1);
            fill_rect(frame,palette,32,264,384,120,0);
            put_opaque(frame,palette,sprites.backdrop,0,32,136);
        }
    }
    const auto& tiles = sprites.second ? sprites.second->tiles :
        (playchar == application::Playchar::reimu ? sprites.reimu_tiles : sprites.marisa_tiles);
    // Full host redraw replaces PC-98 dirty tile/EGC copies. Clip to the
    // original playfield; the scroll ring owns all 400 physical rows.
    for (unsigned y=16; y<384; ++y) {
        for (unsigned x=0; x<384; ++x) {
            if (backdrop) {
                if(npc_active) continue;
                if (background_phase!=(state.elly_active() ? 2 : 1)) continue;
                const int cel=state.orange_background_frame()/2;
                require_view(cel>=0 && cel<16,"Orange BB cel outside resource");
                const unsigned column=x/16,row=(y-16)/16;
                // The actual invalidator redraws stage tiles for ZERO bits.
                // A BB cel is32x32 tiles (four bytes/row); only24x23 show.
                if (((state.kurumi_active() || state.elly_active()) ? sprites.second->assets.transition : sprites.transition)[unsigned(cel)*128+row*4+column/8]&(0x80u>>(column&7))) continue;
            }
            const auto image = sprites.background.image_at(x,y);
            put_indexed_pixel(frame,palette,32,0,x,y,
                tiles.pixel(image,x%16,sprites.background.row_pixel(y)));
        }
    }
    if(npc_active && (npc_background.kind==th04::portable::reimu::BackdropKind::tiles_and_mask || npc_background.kind==th04::portable::reimu::BackdropKind::picture_and_mask)) {
        const unsigned cel=npc_background.cel;require_view(cel<16,"NPC BB cel outside resource");
        for(unsigned row=0;row<23;++row) for(unsigned column=0;column<24;++column)
            if(sprites.second->assets.transition[cel*128+row*4+column/8]&(0x80u>>(column&7)))
                fill_rect(frame,palette,32+int(column*16),16+int(row*16),16,16,15);
    }
    const auto& shots = state.shots().snapshot();
    const auto pixels = [](std::int16_t coordinate) {
        return coordinate >= 0 ? coordinate / 16 : -((-int(coordinate)+15)/16);
    };
    if (state.boss_active()) for (const auto& draw:state.boss_draws()) {
        const auto pattern=draw.pattern_or_radius;
        if(draw.kind==orange::DrawKind::line) {
            const auto points=state.marisa_active() ? th04::portable::marisa::line_pixels({draw.left,draw.top},{draw.end_left,draw.end_top}) : th04::portable::kurumi::ray_pixels({draw.left,draw.top},{draw.end_left,draw.end_top});
            for(auto p:points)
                put_indexed_pixel(frame,palette,p.x,p.y,0,0,draw.color);
        } else if (draw.kind==orange::DrawKind::circle) {
            for (auto p:circle::raster({draw.left,draw.top},pattern)) put_indexed_pixel(frame,palette,p.x,p.y,0,0,draw.color);
        } else if (pattern>=128 && pattern<256) {
            const auto& slot=sprites.stage_slots[pattern];require_view(slot.sheet,"Orange references an empty dynamic stage slot");
            if(state.marisa_active() && (draw.kind==orange::DrawKind::rolling_sprite || draw.kind==orange::DrawKind::white_rolling_sprite))
                th04::portable::marisa::raster_sprite(*slot.sheet,slot.image,draw.left,draw.top,draw.kind,
                    [&](int x,int y) {return frame.indices[unsigned(y)*frame.width+unsigned(x)];},
                    [&](int x,int y,std::uint8_t color) {put_indexed_pixel(frame,palette,x,y,0,0,color);});
            else if(draw.kind==orange::DrawKind::plane_sprite || draw.kind==orange::DrawKind::rolling_sprite)
                put_reimu_sprite(frame,palette,*slot.sheet,slot.image,draw.left,draw.top,draw.kind);
            else put_sprite(frame,palette,*slot.sheet,slot.image,draw.left,draw.top,draw.kind==orange::DrawKind::white_sprite);
        }
        else if (pattern==3) put_sprite(frame,palette,sprites.explosion,0,draw.left,draw.top);
        else if (pattern>=4 && pattern<28) put_sprite(frame,palette,sprites.enemies,pattern-4,draw.left,draw.top,draw.kind==orange::DrawKind::white_rolling_sprite,draw.kind==orange::DrawKind::large_sprite ? 2 : 1);
        else if (pattern>=28 && pattern<128) put_sprite(frame,palette,sprites.items,pattern-28,draw.left,draw.top);
        else throw std::runtime_error("Orange references absent sprite");
    }
    if (state.midboss_state().active) for (const auto& draw:state.midboss_draws()) {
        if (draw.pattern>=128) {
            require_view(draw.pattern<256,"midboss pattern outside stage bank");
            const auto& slot=sprites.stage_slots[draw.pattern];require_view(slot.sheet,"midboss references absent stage sprite");
            put_sprite(frame,palette,*slot.sheet,slot.image,draw.left,draw.top,draw.white);
        } else {
            require_view(draw.pattern>=4 && draw.pattern<28,"midboss references absent defeat sprite");
            put_sprite(frame,palette,sprites.enemies,draw.pattern-4,draw.left,draw.top,draw.white);
        }
    }
    for (const auto& draw:state.enemies().render_sprites()) {
        if (!draw.visible) continue;
        if (draw.pattern>=4 && draw.pattern<28) {
            put_sprite(frame,palette,sprites.enemies,draw.pattern-4,
                       16+pixels(draw.position.x),pixels(draw.position.y),draw.white);
        } else if (draw.pattern>=128) {
            const auto& slot=sprites.stage_slots[draw.pattern];require_view(slot.sheet,"enemy references absent stage sprite");
            put_sprite(frame,palette,*slot.sheet,slot.image,
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
                    put_indexed_pixel(frame,palette,left,16,x,unsigned(y),8+state.frames()%2);
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
        put_sprite(frame,palette,sprites.items,pattern-28,
            32+pixels(entity.position.current.x)-8,16+pixels(entity.position.current.y)-8);
    }
    const auto& position = state.player().position();
    const unsigned cel = position.velocity.x < 0 ? 1 : (position.velocity.x > 0 ? 2 : 0);
    const bool white = state.frames() < 64 && state.frames() % 4 == 0;
    put_sprite(frame, palette,
               playchar == application::Playchar::reimu ? sprites.reimu : sprites.marisa,
               cel, 32 + position.current.x / 16 - 16,
               16 + position.current.y / 16 - 24, white);
    if (shot::level_for_power(state.score().power)>=2) {
        for (int side : {0,48}) {
            put_sprite(frame,palette,sprites.items,
                playchar==application::Playchar::reimu ? 10 : 11,
                pixels(shots.options.x)+side,16+pixels(shots.options.y)-8);
        }
    }
    for (const auto& point:state.gathers().points()) {
        const int left=28+pixels(point.position.x),top=12+pixels(point.position.y);
        for (unsigned y=0;y<8;++y) for (unsigned x=0;x<8;++x) {
            if (gather::pixel(x,y)) put_indexed_pixel(frame,palette,left,top,x,y,point.color);
        }
    }
    for (const auto& entity:state.sparks().snapshot().entities) {
        if (entity.flag!=1) continue;
        const int left=28+pixels(entity.center.current.x),top=12+pixels(entity.center.current.y);
        for (unsigned y=0;y<8;++y) for (unsigned x=0;x<8;++x) {
            if (spark::pixel(entity.age&7u,x,y)) put_indexed_pixel(frame,palette,left,top,x,y,12);
        }
    }
    for (const auto& entity : state.items().entities()) {
        if (entity.flag != th04::portable::item::Flag::alive) continue;
        const auto point = entity.position.current;
        const int x = point.x >= 0 ? point.x / 16 : -((-int(point.x) + 15) / 16);
        const int y = point.y >= 0 ? point.y / 16 : -((-int(point.y) + 15) / 16);
        // 3 player + 1 death + 24 MIKO32 patterns put MIKO16 at global
        // slot 28. IT_POWER is global slot 44, hence local index 16.
        put_sprite(frame, palette, sprites.items,
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
                if (color) put_indexed_pixel(frame,palette,left,top,x,y,color);
            }
        } else if (index<bullet::pellet_count || b.phase<=bullet::Phase::cloud_backward) {
            require_view(b.pattern>=28 && unsigned(b.pattern-28)<sprites.items.count(),"bullet references absent 16px sprite");
            put_sprite(frame,palette,sprites.items,b.pattern-28,24+pixels(p.x),8+pixels(p.y));
        } else if (p.x>=0 && p.x<6144 && p.y>=0 && p.y<5888) {
            const bool blue=b.pattern==54 || b.pattern==55 || b.pattern==57 || (b.pattern>=76 && b.pattern<92);
            const unsigned pattern=(blue ? 19 : 23)+unsigned(b.phase)/4;
            put_sprite(frame,palette,sprites.enemies,pattern-4,16+pixels(p.x),pixels(p.y));
        }
    }
    for (const auto& e:state.circles().snapshot().entities) {
        if (e.flag!=1) continue;
        for (auto p:circle::raster(e.center,static_cast<std::uint16_t>(e.radius)))
            put_indexed_pixel(frame,palette,p.x,p.y,0,0,state.circles().snapshot().color);
    }
    return frame;
}

// TRAM stays bright over the dimmed graphics palette. Writes replace
// entire character cells; blank gaiji also erase preceding text in that cell.
void put_text_requests(Frame& frame,const MainSprites& sprites,const std::vector<th04::portable::bonus::Event>& events) {
    namespace bonus=th04::portable::bonus;
    std::vector<std::uint32_t> layer(640*400,0);
    const auto gaiji_pixel=[&](unsigned glyph,unsigned x,unsigned y) {
        const auto base=32u+unsigned(sprites.gaiji.at(28))+(unsigned(sprites.gaiji.at(29))<<8);
        return (sprites.gaiji.at(base+glyph*32+y*2+x/8)&(0x80u>>(x&7)))!=0;
    };
    for(const auto& e:events) {
        if(e.kind!=bonus::Kind::text && e.kind!=bonus::Kind::gaiji) continue;
        const unsigned color=0xff000000u|((e.color&0x40) ? 0xff0000u : 0)|((e.color&0x80) ? 0xff00u : 0)|((e.color&0x20) ? 0xffu : 0);
        int left=e.left*8;const int top=e.row*16;
        for(unsigned at=0;at<e.bytes.size();) {
            const auto first=static_cast<unsigned char>(e.bytes[at++]);unsigned glyph=first;
            if(e.kind==bonus::Kind::text) {
                require_view(sprites.font.present(),"Text requires the PC-98 font bitmap");
                require_view(at<e.bytes.size(),"Truncated SJIS text");glyph=(glyph<<8)|static_cast<unsigned char>(e.bytes[at++]);
            }
            for(unsigned y=0;y<16;++y) for(unsigned x=0;x<16;++x) {
                const bool set=e.kind==bonus::Kind::text ? sprites.font.pixel(static_cast<std::uint16_t>(glyph),x,y) : gaiji_pixel(glyph,x,y);
                if(left+int(x)>=0 && left+int(x)<640 && top+int(y)>=0 && top+int(y)<400)
                    layer[unsigned(top+int(y))*640+unsigned(left+int(x))]=set ? color : 0;
            }
            left+=16;
        }
    }
    for(unsigned i=0;i<layer.size();++i) if(layer[i]) frame.pixels[i]=layer[i];
}

void put_score_text(Frame& frame,const MainSprites& sprites,const gameplay::State& state) {
    namespace score=th04::portable::score;
    namespace bonus=th04::portable::bonus;
    auto snapshot=state.scoreboard();
    std::vector<bonus::Event> requests;
    for(const auto& e:score::render(snapshot))
        requests.push_back({bonus::Kind::gaiji,int(e.left),int(e.row),int(e.value),0,e.bytes});
    put_text_requests(frame,sprites,requests);
}


void put_stage_overlay(Frame& frame,const MainSprites& sprites,const gameplay::State& state) {
    const auto& cell=state.overlay_cell();
    const bool black=cell.kind==th04::portable::transition::TextKind::character && (cell.attribute&4);
    if(cell.kind==th04::portable::transition::TextKind::character && !black) return;
    const auto base=32u+unsigned(sprites.gaiji.at(28))+(unsigned(sprites.gaiji.at(29))<<8);
    for(unsigned top=16;top<384;top+=16) for(unsigned left=32;left<416;left+=16)
        for(unsigned y=0;y<16;++y) for(unsigned x=0;x<16;++x)
            if(black || (sprites.gaiji.at(base+cell.value*32+y*2+x/8)&(0x80u>>(x&7))))
                frame.pixels[(top+y)*640+left+x]=0xff000000u;
}

class DialogScene {
public:
    DialogScene(MainSprites& sprites,dialog::Script& script,const Frame& frame,unsigned character)
        : sprites_(sprites),script_(script),character_(character),indices_(640*400,255) {
        require_view(sprites_.font.present(),"Dialog requires --font-bmp FILE or a local FREECG98.bmp");
        for(unsigned y=0;y<400;++y) for(unsigned x=0;x<640;++x) {
            const auto pixel=frame.pixels[y*640+x];
            if(pixel==0xff000000u && (x<32 || x>=416 || y<16 || y>=384)) continue;
            if(!frame.indices.empty()) { indices_[y*640+x]=frame.indices[y*640+x];continue; }
            bool found=false;
            for(unsigned color=0;color<16;++color) if(pixel==palette_color(sprites_.palette,color)) { indices_[y*640+x]=static_cast<std::uint8_t>(color);found=true;break; }
            require_view(found,"dialog snapshot pixel is outside the active palette");
        }
    }
    void advance(std::uint16_t held) {
        if(intro_<36) {
            boxes(intro_/12);++intro_;
            if(intro_==36) { back_=indices_;script_.begin(); }
            return;
        }
        script_.advance(held,[&](const dialog::Event& event) { events_.push_back(event);apply(event); });
    }
    bool finished() const { return intro_==36 && script_.status()==dialog::Status::stopped; }
    dialog::Status status() const { return intro_==36 ? script_.status() : dialog::Status::delay; }
    unsigned glyph_count() const { return static_cast<unsigned>(glyphs_.size()); }
    const std::vector<dialog::Event>& events() const { return events_; }
    bool boss_portrait_visible() const {
        return std::any_of(events_.begin(),events_.end(),[](const dialog::Event& e) {
            return e.kind==dialog::Kind::face && e.a==288;
        });
    }
    Frame render() const {
        Frame frame{640,400,std::vector<std::uint32_t>(640*400,0xff000000u)};
        PiImage palette=sprites_.palette;const int tone=script_.tone();
        for(auto& component:palette.palette) {
            const int base=component>>4;
            component=static_cast<std::uint8_t>((tone<=100 ? base*tone/100 : 15-(15-base)*(200-tone)/100)*16);
        }
        for(unsigned i=0;i<indices_.size();++i) if(indices_[i]!=255) frame.pixels[i]=palette_color(palette,indices_[i]);
        // PC-98 TRAM text is a separate layer and does not follow the analog
        // graphics palette fade. All script text/gaiji uses TX_WHITE.
        for(const auto& glyph:glyphs_) for(unsigned y=0;y<16;++y) for(unsigned x=0;x<16;++x) {
            bool set=false;
            if(glyph.kind==dialog::Kind::text) set=sprites_.font.pixel(static_cast<std::uint16_t>(glyph.c),x,y);
            else {
                const auto& bytes=sprites_.gaiji;
                const unsigned base=32u+unsigned(bytes.at(28))+(unsigned(bytes.at(29))<<8);
                if(glyph.c>=0 && glyph.c<256) set=(bytes.at(base+unsigned(glyph.c)*32+y*2+x/8)&(0x80u>>(x&7)))!=0;
            }
            if(set && glyph.a+int(x)>=0 && glyph.a+int(x)<640 && glyph.b+int(y)>=0 && glyph.b+int(y)<400)
                frame.pixels[unsigned(glyph.b+int(y))*640+unsigned(glyph.a+int(x))]=0xffffffffu;
        }
        return frame;
    }
private:
    void pixel(int x,int y,unsigned color) { if(x>=0 && x<640 && y>=0 && y<400) indices_[unsigned(y)*640+unsigned(x)]=static_cast<std::uint8_t>(color); }
    void boxes(unsigned density) {
        for(auto origin:{std::pair<int,int>{48,192},{80,320}}) for(unsigned y=0;y<48;++y) for(unsigned x=0;x<320;++x)
            if(((x-y)&3u)<=density) pixel(origin.first+int(x),origin.second+int(y),1);
    }
    void apply(const dialog::Event& e) {
        switch(e.kind) {
        case dialog::Kind::box:
            glyphs_.erase(std::remove_if(glyphs_.begin(),glyphs_.end(),[&](const dialog::Event& glyph) { return glyph.a>=e.a && glyph.a<e.a+240 && glyph.b>=e.b && glyph.b<e.b+48; }),glyphs_.end());break;
        case dialog::Kind::text:case dialog::Kind::gaiji:glyphs_.push_back(e);break;
        case dialog::Kind::face_clear: {
            for(unsigned y=0;y<128;++y) for(unsigned x=0;x<128;++x) pixel(e.a+int(x),e.b+int(y),back_.at(unsigned(e.b+int(y))*640+unsigned(e.a+int(x))));
            break;
        }
        case dialog::Kind::face: {
            const auto& sheet=e.a==32 ? (character_ ? sprites_.marisa_faces : sprites_.reimu_faces) : sprites_.boss_portraits();
            const unsigned image=static_cast<unsigned>(e.c-(e.a==32 ? 2 : 8));
            require_view(image<sheet.image_count,"dialog references absent portrait");
            for(unsigned y=0;y<128;++y) for(unsigned x=0;x<128;++x) if(sheet.bit(image,0,x,y)) {
                unsigned color=0;for(unsigned plane=0;plane<4;++plane) if(sheet.bit(image,plane+1,x,y)) color|=1u<<plane;
                pixel(e.a+int(x),e.b+int(y),color);
            }break;
        }
        case dialog::Kind::sprite: {
            require_view(e.c>=128 && e.c<256,"dialog sprite is outside the current stage bank");const auto& slot=sprites_.stage_slots[unsigned(e.c)];require_view(slot.sheet,"dialog references absent sprite");
            for(unsigned y=0;y<slot.sheet->height();++y) for(unsigned x=0;x<slot.sheet->width();++x) {
                const auto color=slot.sheet->pixel(slot.image,x,y);if(color) pixel(e.a+int(x),(e.b+int(y))%400,color);
            }break;
        }
        case dialog::Kind::clean:sprites_.clean_stage();break;
        case dialog::Kind::sprite_load:sprites_.load_dialog_sprites(e.name);break;
        case dialog::Kind::cdg_free:throw std::runtime_error("Stage 1 dialog unexpectedly frees a CDG slot");
        default:break; // Timing/palette is Script-owned; audio/overlay requests are retained.
        }
    }
    MainSprites& sprites_;dialog::Script& script_;unsigned character_,intro_=0;
    Bytes indices_,back_;std::vector<dialog::Event> glyphs_,events_;
};

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
        assets_=main_assets;
        if (main_assets && !main_assets->reimu.empty()) {
            sprites_ = std::make_unique<MainSprites>(*main_assets);
        }
    }

    void enable_stage2() { continue_stage2_=true; }
    void enable_kurumi() { continue_stage2_=true;continue_kurumi_=true; }
    void enable_stage3() { enable_kurumi();continue_stage3_=true; }
    void enable_elly() { enable_stage3();continue_elly_=true; }
    void enable_stage4() { enable_elly();continue_stage4_=true; }
    void enable_reimu() { enable_stage4();continue_reimu_=true; }
    void enable_marisa() { enable_stage4();continue_marisa_=true; }
    bool stage4_dialog_complete() const { return fourth_pre_finished_; }
    bool stage3_dialog_complete() const { return third_pre_finished_; }
    unsigned resource_stage() const { return loaded_stage_; }
    bool stage2_dialog_complete() const { return second_pre_finished_; }
    bool boss_portrait_visible() const { return dialog_scene_ && dialog_scene_->boss_portrait_visible(); }
    bool stage2_resources_valid() const {
        if(!sprites_->second || sprites_->stage_end!=162 || application_.resident().resource_stage!=1) return false;
        for(unsigned i=128;i<162;++i) if(!sprites_->stage_slots[i].sheet) return false;
        for(unsigned i=162;i<256;++i) if(sprites_->stage_slots[i].sheet) return false;
        return true;
    }
    bool stage4_resources_valid() const {
        if(!sprites_->second || sprites_->stage_end!=164 || application_.resident().resource_stage!=3) return false;
        for(unsigned i=128;i<164;++i) if(!sprites_->stage_slots[i].sheet) return false;
        for(unsigned i=164;i<256;++i) if(sprites_->stage_slots[i].sheet) return false;
        return sprites_->second->faces.image_count==(application_.resident().playchar==application::Playchar::reimu ? 4u : 3u);
    }
    bool stage4_battle_resources_valid() const {
        const bool reimu=application_.resident().playchar==application::Playchar::reimu;
        const auto first=sprites_->stage_slots[128],second=sprites_->stage_slots[reimu ? 136 : 140];
        return sprites_->stage_end==(reimu ? 140u : 148u) && first.sheet && second.sheet &&
            first.sheet->width()==64 && first.sheet->height()==64 && first.sheet->count()==(reimu ? 8u : 12u) &&
            second.sheet->width()==32 && second.sheet->height()==32 && second.sheet->count()==(reimu ? 4u : 8u);
    }
    bool carpet_active() const { return sprites_->second && sprites_->second->carpet.active; }
    bool stage3_resources_valid() const {
        if(!sprites_->second || sprites_->stage_end!=148 || application_.resident().resource_stage!=2) return false;
        for(unsigned i=128;i<148;++i) if(!sprites_->stage_slots[i].sheet) return false;
        for(unsigned i=148;i<256;++i) if(sprites_->stage_slots[i].sheet) return false;
        return true;
    }
    bool stage3_battle_resources_valid() const {
        const auto first=sprites_->stage_slots[128],second=sprites_->stage_slots[134];
        return sprites_->stage_end==146 && first.sheet && second.sheet && first.sheet->count()==6 && first.sheet->width()==32 && first.sheet->height()==32 && second.sheet->count()==12 && second.sheet->width()==64 && second.sheet->height()==64;
    }
    const Frame& frame() const { return frame_; }
    bool live_main() const { return screen_ == Screen::main_handoff && bool(main_); }
    unsigned slowdown() const { return main_ && !dialog_scene_ ? main_->slowdown() : 1; }
    bool dialog_active() const { return bool(dialog_scene_); }
    bool post_dialog_complete() const { return post_finished_; }
    bool post_dialog() const { return post_started_; }
    const application::ResidentState& resident() const { return application_.resident(); }
    std::uint32_t process_random_state() const { return application_.process_random_state(); }
    unsigned generation() const { return application_.generation(); }
    unsigned dialog_glyphs() const { return dialog_scene_ ? dialog_scene_->glyph_count() : 0; }
    dialog::Status dialog_status() const { return dialog_scene_ ? dialog_scene_->status() : dialog::Status::idle; }
    std::size_t dialog_offset() const { return script_ ? script_->offset() : 0; }
    bool battle_resources_valid() const {
        const auto first=sprites_->stage_slots[128],second=sprites_->stage_slots[132];
        return sprites_->stage_end==140 && first.sheet && second.sheet && first.sheet->width()==32 && first.sheet->height()==48 && first.sheet->count()==4 && second.sheet->width()==64 && second.sheet->height()==80 && second.sheet->count()==8;
    }
    void advance(std::uint16_t held_input, bool shift,bool repaint=true) {
        if (live_main()) {
            if(main_->next_stage_requested() && ((continue_stage2_ && loaded_stage_==0) || (continue_stage3_ && loaded_stage_==1) || (continue_stage4_ && loaded_stage_==2))) {
                const auto next_id=loaded_stage_+1;
                require_view(bool(assets_),"next-stage resources missing");
                const auto& resources=next_id==1 ? assets_->stage2 : (next_id==2 ? assets_->stage3 : assets_->stage4[unsigned(application_.resident().playchar)]);
                auto next=std::make_unique<StageSprites>(resources,next_id);
                auto script=std::make_unique<dialog::Script>(next->assets.dialog_scripts[unsigned(application_.resident().playchar)]);
                main_->prepare_next_stage_actors(next->assets.standard);
                sprites_->install_stage(std::move(next));script_=std::move(script);
                loaded_stage_=next_id;post_started_=post_finished_=false;
                application_.publish_main_resource_stage(static_cast<std::uint8_t>(next_id));
            }
            if(loaded_stage_==3 && !dialog_scene_ && !fourth_pre_finished_ && main_->stage4_dialog_ready(sprites_->background)) begin_dialog(false);
            if(loaded_stage_==2 && !dialog_scene_ && !third_pre_finished_ && main_->stage3_dialog_ready(sprites_->background)) begin_dialog(false);
            if(loaded_stage_==1 && !dialog_scene_ && !second_pre_finished_ && main_->stage2_dialog_ready(sprites_->background)) begin_dialog(false);
            if(!diagnostic_ && !dialog_scene_ && main_->stage1_dialog_ready(sprites_->background)) begin_dialog(false);
            if(!diagnostic_ && !dialog_scene_ && !post_started_ && main_->boss_active() && main_->boss_snapshot().phase==255 && main_->boss_snapshot().phase_frame==0) {
                main_->update(held_input,shift,false,0,&sprites_->background);begin_dialog(true);
            }
            if(dialog_scene_) {
                dialog_scene_->advance(held_input);
                if(dialog_scene_->finished()) {
                    if(post_started_) { post_finished_=true;main_->finish_post_boss_dialog(); }
                    else if(loaded_stage_==3) { fourth_pre_finished_=true;if(continue_reimu_ && application_.resident().playchar==application::Playchar::marisa) {
                        require_view(stage4_battle_resources_valid(),"Reimu battle sprite bank invalid");
                        main_->start_reimu_after_dialog({sprites_->palette.palette[0],sprites_->palette.palette[1],sprites_->palette.palette[2]});
                    } else if(continue_marisa_ && application_.resident().playchar==application::Playchar::reimu) {
                        require_view(stage4_battle_resources_valid(),"Marisa battle sprite bank invalid");
                        main_->start_marisa_after_dialog({sprites_->palette.palette[0],sprites_->palette.palette[1],sprites_->palette.palette[2]});
                    } }
                    else if(loaded_stage_==2) { third_pre_finished_=true;if(continue_elly_) main_->start_elly_after_dialog({sprites_->palette.palette[0],sprites_->palette.palette[1],sprites_->palette.palette[2]}); }
                    else if(loaded_stage_==1) { second_pre_finished_=true;if(continue_kurumi_) main_->start_kurumi_after_dialog({sprites_->palette.palette[0],sprites_->palette.palette[1],sprites_->palette.palette[2]}); }
                    else { require_view(sprites_->stage_end==140,"Stage 1 dialog did not install the twelve battle sprites");main_->start_orange_after_dialog(); }
                    dialog_scene_.reset();
                } else { if(repaint) frame_=render();return; }
            }
            const auto before=main_->frames();
            main_->update(held_input, shift, false, sprites_->background.last_delta(),&sprites_->background);
            if(main_->frames()!=before && !main_->next_stage_requested()) {
                if(loaded_stage_==3) th04::portable::stage4::update_carpet(sprites_->second->carpet,
                    sprites_->background.mutable_ring(),static_cast<std::uint16_t>(before),sprites_->background.scroll_line());
                sprites_->background.update();
            }
            if (repaint) frame_ = render();
        }
        else if (screen_ == Screen::menu) application_.advance_op_menu_frame();
    }
    void repaint() { frame_=render(); }
    void diagnostic_start_orange() {
        require_view(live_main(),"Orange fixture requires MAIN");
        diagnostic_=true;sprites_->diagnostic_boss_sprites();sprites_->background.set_speed(0);main_->start_orange_after_dialog();
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
                    script_=std::make_unique<dialog::Script>(sprites_->scripts[unsigned(result.playchar)]);
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
            if (pressed == menu::Input::cancel && !dialog_scene_) {
                close = true;
            }
            break;
        }
        frame_ = render();
        return close;
    }

private:
    void begin_dialog(bool post) {
        post_started_=post;dialog_scene_=std::make_unique<DialogScene>(*sprites_,*script_,render_main(*sprites_,*main_,application_.resident().playchar,main_->palette_tone_before_frame()),unsigned(application_.resident().playchar));
    }
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
            if(dialog_scene_) { auto frame=dialog_scene_->render();put_score_text(frame,*sprites_,*main_);return frame; }
            if(main_) {
                auto frame=render_main(*sprites_,*main_,application_.resident().playchar);
                if(main_->clear_bonus()) {
                    // Departure already publishes graphics tone60 once; TRAM stays bright.
                    if(main_->bonus_text_visible()) put_text_requests(frame,*sprites_,main_->clear_bonus()->events);
                }
                put_stage_overlay(frame,*sprites_,*main_);
                put_score_text(frame,*sprites_,*main_);
                return frame;
            }
            return render_main_handoff(
                selection_background_, portraits_, application_
            );
        }
        throw std::logic_error("invalid portable front-end screen");
    }

    const MainAssets* assets_=nullptr;
    bool continue_stage2_=false,continue_kurumi_=false,second_pre_finished_=false;
    bool continue_stage3_=false,third_pre_finished_=false,continue_elly_=false;
    bool continue_stage4_=false,fourth_pre_finished_=false,continue_reimu_=false,continue_marisa_=false;
    unsigned loaded_stage_=0;
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
    std::unique_ptr<dialog::Script> script_;
    std::unique_ptr<DialogScene> dialog_scene_;
    bool diagnostic_=false,post_started_=false,post_finished_=false;
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
                  selection_background_, portraits_, &main_assets) { front_end.enable_reimu();front_end.enable_marisa(); }

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
                if (active && GetAsyncKeyState(VK_RETURN) & 0x8000) held |= 0x1000;
                if (active && GetAsyncKeyState('X') & 0x8000) held |= 0x800;
                if (active && GetAsyncKeyState(VK_ESCAPE) & 0x8000) held |= 0x2000;
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
        0, class_name, L"TH04 native x64 reconstruction - Stage1/Stage2 preview",
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
        "TH04 native x64 reconstruction - Stage1/Stage2 preview", SDL_WINDOWPOS_CENTERED,
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
    front_end.enable_reimu();front_end.enable_marisa();
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
                if (keys[SDL_SCANCODE_RETURN]) held |= 0x1000;
                if (keys[SDL_SCANCODE_X]) held |= 0x800;
                if (keys[SDL_SCANCODE_ESCAPE]) held |= 0x2000;
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
    const std::string& combat_screenshots,const std::string& midboss_screenshots,
    const std::string& orange_screenshots,const std::string& dialog_screenshots,
    const std::string& stage2_screenshots,const std::string& kurumi_screenshots,const std::string& stage3_screenshots,const std::string& elly_screenshots,const std::string& stage4_screenshots,const std::string& reimu_screenshots,const std::string& marisa_screenshots, bool window
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
                      << " score=" << state.awarded_score_units() << " power=" << +state.score().power
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
    if (!midboss_screenshots.empty()) {
        for (unsigned character=0;character<2;++character) for (unsigned shooting=0;shooting<2;++shooting) {
            FrontEnd scene(background,numerals,labels,cursors,selection_background,portraits,&main_assets);
            scene.input(menu::Input::confirm);
            if (character) scene.input(menu::Input::right);
            scene.input(menu::Input::confirm);scene.input(menu::Input::confirm);
            bool appeared=false,unfolded=false,attacked=false,finished=false;
            for (unsigned frame=0;frame<4500;++frame) {
                scene.advance(shooting ? shot::input_shot : 0,false);
                const auto& state=scene.main_state();const auto& boss=state.midboss().snapshot();
                appeared|=boss.active;unfolded|=boss.active && boss.phase==1;
                attacked|=boss.active && boss.phase==3;finished|=appeared && !boss.active;
                if (frame==3100 || frame==3387 || frame==3483 || frame==3516 || frame==3999 || frame==4499) {
                    const auto name=std::string(character ? "marisa" : "reimu")+(shooting ? "-shot-" : "-idle-")+std::to_string(frame+1);
                    const auto path=midboss_screenshots+"/"+name+".bmp";write_bmp(path,scene.frame());
                    unsigned alive=0;for (const auto& bullet:state.bullets().snapshot().entities) alive+=bullet.flag==1;
                    std::cout << "MAIN midboss case=" << name << " active=" << boss.active << " phase=" << +boss.phase
                              << " hp=" << boss.hp << " bullets=" << alive << " score=" << state.awarded_score_units()
                              << " screenshot=" << path << '\n';
                }
            }
            require_view(appeared && unfolded && attacked,"Stage 1 midboss progression was not reached");
            require_view(finished,"Stage 1 midboss did not leave the scene");
            require_view(scene.main_state().midboss().score_delta()==(shooting ? 6400u : 0u),
                         "Stage 1 shooting/timeout outcome differs");
        }
    }
    if (!orange_screenshots.empty()) {
        for (unsigned lunatic=0;lunatic<2;++lunatic) for (unsigned character=0;character<2;++character) for (unsigned shooting=0;shooting<2;++shooting) {
            FrontEnd scene(background,numerals,labels,cursors,selection_background,portraits,&main_assets);
            if (lunatic) {
                for (unsigned i=0;i<3;++i) scene.input(menu::Input::down);
                scene.input(menu::Input::confirm);scene.input(menu::Input::right);scene.input(menu::Input::right);
                scene.input(menu::Input::cancel);
                for (unsigned i=0;i<3;++i) scene.input(menu::Input::up);
            }
            scene.input(menu::Input::confirm);
            if (character) scene.input(menu::Input::right);
            scene.input(menu::Input::confirm);scene.input(menu::Input::confirm);
            // Explicit diagnostic boundary: no ordinary pre-boss dialog is
            // claimed. Keep normal initial power, real shots/items/RNG, and
            // stopped scrolling; only bypass the unported dialog consumer.
            scene.diagnostic_start_orange();std::array<bool,256> seen{};
            const std::array<std::pair<unsigned,int>,7> checkpoints{{{0,192},{1,16},{2,96},{3,256},{4,160},{254,8},{254,16}}};
            std::array<bool,7> captured{};
            for (unsigned frame=0;frame<6000;++frame) {
                scene.advance(shooting ? shot::input_shot : 0,false,false);
                const auto& state=scene.main_state();const auto& boss=state.boss_snapshot();
                const bool first=!seen[boss.phase];
                int checkpoint=-1;
                for (unsigned i=0;i<checkpoints.size();++i) {
                    if (!captured[i] && boss.phase==checkpoints[i].first && boss.phase_frame==checkpoints[i].second) {
                        checkpoint=static_cast<int>(i);captured[i]=true;break;
                    }
                }
                if (first || checkpoint>=0) {
                    seen[boss.phase]=true;
                    const auto age=boss.big.age;const auto clock=boss.big_frame;const auto simulation=state.frames();
                    scene.repaint();scene.repaint();
                    require_view(age==state.boss_snapshot().big.age && clock==state.boss_snapshot().big_frame && simulation==state.frames(),"repaint advanced Orange simulation");
                    const auto name=std::string(lunatic ? "lunatic-" : "normal-")+(character ? "marisa-" : "reimu-")+(shooting ? "shot-" : "idle-")+std::to_string(boss.phase)+(first ? "" : "-at-"+std::to_string(boss.phase_frame));
                    const auto path=orange_screenshots+"/"+name+".bmp";write_bmp(path,scene.frame());
                    unsigned alive=0;for (const auto& b:state.bullets().snapshot().entities) alive+=b.flag==1;
                    std::cout << "MAIN Orange fixture=" << name << " frame=" << state.frames() << " hp=" << boss.hp
                              << " bullets=" << alive << " bonus=" << boss.score_delta << " screenshot=" << path << '\n';
                }
                if (state.post_boss_dialog_pending()) break;
            }
            for (unsigned phase:{0,1,2,3,4,5,254,255}) require_view(seen[phase],"Orange fixture missed a Boss phase");
            for (bool capture:captured) require_view(capture,"Orange fixture missed an attack/explosion checkpoint");
            require_view(scene.main_state().post_boss_dialog_pending(),"Orange fixture did not stop at post-boss dialog");
            const auto bonus=scene.main_state().orange().snapshot().score_delta;
            require_view(shooting ? bonus>0 : bonus==0,"Orange shot/timeout reward differs");
            const auto stopped_frame=scene.main_state().frames();
            for (unsigned i=0;i<3;++i) scene.advance(shot::input_shot,false,false);
            require_view(scene.main_state().frames()==stopped_frame && scene.main_state().orange().snapshot().phase_frame==0,
                         "pending post-boss dialog advanced simulation");
            std::cout << "MAIN Orange stopped rank=" << (lunatic ? "Lunatic" : "Normal") << " character=" << character
                      << " shooting=" << shooting << " frames=" << scene.main_state().frames() << " bonus=" << bonus << " dialog=pending\n";
        }
    }
    if (!dialog_screenshots.empty()) {
        for(unsigned lunatic=0;lunatic<2;++lunatic) for(unsigned character=0;character<2;++character) for(unsigned shooting=0;shooting<2;++shooting) {
            FrontEnd scene(background,numerals,labels,cursors,selection_background,portraits,&main_assets);
            if(lunatic) {
                for(unsigned i=0;i<3;++i) scene.input(menu::Input::down);
                scene.input(menu::Input::confirm);scene.input(menu::Input::right);scene.input(menu::Input::right);scene.input(menu::Input::cancel);
                for(unsigned i=0;i<3;++i) scene.input(menu::Input::up);
            }
            scene.input(menu::Input::confirm);if(character) scene.input(menu::Input::right);
            scene.input(menu::Input::confirm);scene.input(menu::Input::confirm);
            std::array<bool,8> seen{};std::uint32_t start_frame=0,clear_frame=0;unsigned frozen_ticks=0,bonuses=0,fades=0,next=0;
            const auto process_random=scene.process_random_state();
            const auto actor_stamp=[&]() {
                const auto& state=scene.main_state();const auto& shots=state.shots().snapshot();
                std::vector<int> stamp{state.player().position().current.x,state.player().position().current.y,shots.time,shots.reimu_cycle,shots.laser.time,shots.laser.bottom.current.x,shots.laser.bottom.current.y};
                for(const auto& e:shots.entities) { stamp.push_back(e.flag);stamp.push_back(e.age);stamp.push_back(e.position.current.x);stamp.push_back(e.position.current.y); }
                return stamp;
            };
            for(unsigned tick=0;tick<20000;++tick) {
                const bool blocked=scene.dialog_active();const auto before=scene.main_state().frames();const auto random=scene.main_state().random_cursor();const auto actors=actor_stamp();const bool post=scene.post_dialog();
                const std::uint16_t input=blocked ? (scene.dialog_status()==dialog::Status::press ? 0x1000 : 0) : (shooting ? shot::input_shot : 0);
                scene.advance(input,false,false);
                if(blocked && scene.dialog_active()) {
                    require_view(scene.main_state().frames()==before && scene.main_state().random_cursor()==random,"dialog advanced game frame or shared RNG");require_view(actor_stamp()==actors,"dialog updated player or shot actors");++frozen_ticks;
                }
                if(blocked && post && !scene.dialog_active()) require_view(actor_stamp()==actors,"resumed post-dialog frame repeated its actor prefix");
                const auto& state=scene.main_state();int checkpoint=-1;
                if(state.frames()!=before) for(const auto& e:state.orange_events()) {
                    if(e.type==orange::EventType::stage_bonus) ++bonuses;
                    if(e.type==orange::EventType::fade) { ++fades;require_view(state.boss_snapshot().phase_frame==417 && state.overlay().time==71,"fade did not start at416 before overlay decrement"); }
                    if(e.type==orange::EventType::next_stage) { ++next;require_view(state.boss_snapshot().phase_frame==489,"next-stage request did not complete frame488"); }
                }
                if(!seen[0] && scene.dialog_active() && !scene.post_dialog() && scene.dialog_status()==dialog::Status::release) { checkpoint=0;start_frame=state.frames(); }
                else if(!seen[1] && state.boss_active()) { checkpoint=1;require_view(seen[0] && scene.battle_resources_valid(),"ordinary Boss activated before dialog/resources completed"); }
                else if(!seen[2] && state.boss_active() && state.boss_snapshot().phase==2) checkpoint=2;
                else if(!seen[3] && scene.dialog_active() && scene.post_dialog() && scene.dialog_status()==dialog::Status::release) checkpoint=3;
                else if(!seen[4] && scene.post_dialog_complete()) { checkpoint=4;clear_frame=state.frames(); }
                else if(!seen[5] && scene.post_dialog_complete() && state.boss_snapshot().phase==255 && state.boss_snapshot().phase_frame==417) checkpoint=5;
                else if(!seen[6] && scene.post_dialog_complete() && state.boss_snapshot().phase==255 && state.boss_snapshot().phase_frame==481) checkpoint=6;
                else if(!seen[7] && state.next_stage_requested()) checkpoint=7;
                if(checkpoint>=0) {
                    seen[unsigned(checkpoint)]=true;scene.repaint();
                    const auto name=std::string(lunatic ? "lunatic-" : "normal-")+(character ? "marisa-" : "reimu-")+(shooting ? "shot-" : "idle-")+std::to_string(checkpoint);
                    const auto path=dialog_screenshots+"/"+name+".bmp";write_bmp(path,scene.frame());
                    std::cout<<"MAIN dialog fixture="<<name<<" frame="<<state.frames()<<" offset="<<scene.dialog_offset()<<" power="<<+state.score().power<<" bonus="<<state.boss_snapshot().score_delta<<" screenshot="<<path<<'\n';
                }
                if(state.next_stage_requested()) break;
            }
            for(bool capture:seen) require_view(capture,"natural Stage 1 dialog fixture missed progression");
            require_view(start_frame>4500 && !(start_frame&1) && frozen_ticks>100,"dialog was not naturally gated by stopped scroll/back page");
            require_view(bool(scene.main_state().clear_bonus()),"Post-dialog did not consume stage-clear bonus");
            require_view(bonuses==1 && fades==1 && next==1,"departure callback consumed more than once");
            const auto stopped=scene.main_state().frames();const auto actors=actor_stamp();const auto random=scene.main_state().random_cursor();
            const auto pending=scene.main_state().score().score_delta;
            for(unsigned i=0;i<3;++i) scene.advance(shot::input_shot|player::left,false,false);
            require_view(scene.main_state().frames()==stopped && actor_stamp()==actors && scene.main_state().random_cursor()==random && scene.main_state().score().score_delta==pending,"unloaded Stage2 request repeated simulation");
            require_view(stopped-clear_frame==488 && scene.resident().stage==1 && scene.resident().stage_ascii=='1',"departure frame or resident stage/ascii differs");
            require_view(scene.resident().resource_stage==0 && scene.process_random_state()==process_random,"next-stage request replaced resources or reseeded MAIN early");
            require_view(scene.main_state().overlay().callback==th04::portable::transition::Callback::none && !scene.main_state().bonus_text_visible(),"final leave did not replace bonus TRAM with black cells");
            require_view(scene.resident().remaining_lives==scene.main_state().score().remaining_lives && scene.resident().remaining_bombs==scene.main_state().score().remaining_bombs,"resident resources did not follow completed-frame awards");
            std::cout<<"MAIN dialog stopped character="<<character<<" rank="<<(lunatic ? "Lunatic" : "Normal")<<" shooting="<<shooting<<" entry_frame="<<start_frame<<" frames="<<stopped<<" frozen_ticks="<<frozen_ticks<<" stage_clear=bonus_complete awarded="<<scene.main_state().clear_bonus()->awarded<<" bombs="<<+scene.main_state().score().remaining_bombs<<" departure_frames="<<stopped-clear_frame<<" pending="<<pending<<" stage="<<+scene.resident().stage<<" graze="<<scene.resident().graze<<" progression=next_stage_resources_pending\n";
        }
    }
    if (!stage2_screenshots.empty()) {
        for(unsigned lunatic=0;lunatic<2;++lunatic) for(unsigned character=0;character<2;++character) {
            FrontEnd scene(background,numerals,labels,cursors,selection_background,portraits,&main_assets);
            scene.enable_stage2();
            if(lunatic) {
                for(unsigned i=0;i<3;++i) scene.input(menu::Input::down);
                scene.input(menu::Input::confirm);scene.input(menu::Input::right);scene.input(menu::Input::right);
                scene.input(menu::Input::cancel);for(unsigned i=0;i<3;++i) scene.input(menu::Input::up);
            }
            scene.input(menu::Input::confirm);if(character) scene.input(menu::Input::right);
            scene.input(menu::Input::confirm);scene.input(menu::Input::confirm);
            std::array<bool,8> seen{};unsigned frozen=0,loads=0,draws=0;
            const auto generation=scene.generation();
            const auto actor_stamp=[&]() {
                const auto& state=scene.main_state();const auto& shots=state.shots().snapshot();
                std::vector<int> result{state.player().position().current.x,state.player().position().current.y,shots.time,shots.reimu_cycle,shots.laser.time};
                for(const auto& s:shots.entities) { result.push_back(s.flag);result.push_back(s.age);result.push_back(s.position.current.x);result.push_back(s.position.current.y); }
                return result;
            };
            for(unsigned tick=0;tick<30000 && !scene.stage2_dialog_complete();++tick) {
                const auto resource=scene.resource_stage();const auto before=scene.main_state().frames();
                const auto random=scene.main_state().random_cursor();const auto actors=actor_stamp();
                const auto process=scene.process_random_state();const bool blocked=scene.dialog_active();
                scene.advance(blocked ? (scene.dialog_status()==dialog::Status::press ? 0x1000 : 0) : shot::input_shot,false,false);
                const auto& state=scene.main_state();
                if(blocked && (scene.dialog_active() || scene.stage2_dialog_complete())) {
                    require_view(state.frames()==before && state.random_cursor()==random && actor_stamp()==actors,"Stage2 dialog changed gameplay actors/clock/RNG");++frozen;
                }
                if(resource==0 && scene.resource_stage()==1) {
                    ++loads;th04::portable::rng::Lcg32 expected(process);
                    for(unsigned i=0;i<353;++i) expected.next_byte();
                    require_view(scene.process_random_state()==expected.state() && scene.generation()==generation,
                                 "Stage2 resource installation restarted MAIN or consumed the wrong process RNG draws");
                }
                if(scene.resource_stage()!=1) continue;
                require_view(scene.stage2_resources_valid(),"Stage2 retained old sprite slots or published inconsistent resources");
                if(state.frames()!=before && state.midboss_state().active) draws+=static_cast<unsigned>(state.midboss_draws().size());
                const auto& boss=state.midboss_state();int checkpoint=-1;
                if(!seen[0] && state.frames()==1) checkpoint=0;
                else if(!seen[1] && state.frames()==80) checkpoint=1;
                else if(!seen[2] && boss.active && boss.phase==0 && boss.phase_frame==64) checkpoint=2;
                else if(!seen[3] && boss.active && boss.phase==1 && boss.phase_frame==32) checkpoint=3;
                else if(!seen[4] && boss.active && boss.phase==2 && boss.phase_frame==8) checkpoint=4;
                else if(!seen[5] && scene.dialog_active() && scene.dialog_status()==dialog::Status::release) checkpoint=5;
                else if(!seen[6] && scene.dialog_active() && scene.dialog_status()==dialog::Status::release && scene.boss_portrait_visible()) checkpoint=6;
                else if(!seen[7] && scene.stage2_dialog_complete()) checkpoint=7;
                if(checkpoint>=0) {
                    seen[unsigned(checkpoint)]=true;scene.repaint();
                    if(checkpoint>=5) require_view(state.frames()==6982u,"Stage2 dialog did not stop at its natural STD gate");
                    const auto name=std::string(lunatic ? "lunatic-" : "normal-")+(character ? "marisa-" : "reimu-")+std::to_string(checkpoint);
                    const auto path=stage2_screenshots+"/"+name+".bmp";write_bmp(path,scene.frame());
                    std::cout<<"MAIN Stage2 fixture="<<name<<" frame="<<state.frames()<<" phase="<<+boss.phase<<" hp="<<boss.hp
                             <<" offset="<<scene.dialog_offset()<<" power="<<+state.score().power<<" pending="<<state.score().score_delta
                             <<" rng="<<scene.process_random_state()<<" screenshot="<<path<<'\n';
                }
            }
            for(bool capture:seen) require_view(capture,"natural Stage2 fixture missed a visual progression checkpoint");
            require_view(loads==1 && draws>500 && frozen>100 && scene.stage2_dialog_complete(),"Stage2 load/midboss/dialog progression missing");
            const auto frames=scene.main_state().frames();const auto random=scene.main_state().random_cursor();
            const auto actors=actor_stamp();const auto offset=scene.dialog_offset();
            for(unsigned i=0;i<3;++i) scene.advance(shot::input_shot|player::left,false,false);
            require_view(scene.main_state().frames()==frames && scene.main_state().random_cursor()==random && actor_stamp()==actors &&
                         scene.dialog_offset()==offset && !scene.dialog_active(),"unported Kurumi frontier restarted dialog or gameplay");
            std::cout<<"MAIN Stage2 stopped character="<<character<<" rank="<<(lunatic ? "Lunatic" : "Normal")<<" frames="<<frames
                     <<" frozen_ticks="<<frozen<<" loads="<<loads<<" midboss_draws="<<draws<<" generation="<<scene.generation()
                     <<" sprite_end=162 progression=kurumi_battle_pending\n";
        }
    }
    if (!kurumi_screenshots.empty()) {
        for(unsigned lunatic=0;lunatic<2;++lunatic) for(unsigned character=0;character<2;++character) for(unsigned shooting=0;shooting<2;++shooting) {
            FrontEnd scene(background,numerals,labels,cursors,selection_background,portraits,&main_assets);
            scene.enable_kurumi();
            if(lunatic) {
                for(unsigned i=0;i<3;++i) scene.input(menu::Input::down);
                scene.input(menu::Input::confirm);scene.input(menu::Input::right);scene.input(menu::Input::right);
                scene.input(menu::Input::cancel);for(unsigned i=0;i<3;++i) scene.input(menu::Input::up);
            }
            scene.input(menu::Input::confirm);if(character) scene.input(menu::Input::right);
            scene.input(menu::Input::confirm);scene.input(menu::Input::confirm);
            std::array<bool,9> seen{};unsigned frozen=0,bonuses=0,fades=0,next=0,ray_frames=0;
            std::uint32_t clear_frame=0;
            const auto generation=scene.generation();
            const auto actor_stamp=[&]() {
                const auto& state=scene.main_state();const auto& shots=state.shots().snapshot();
                std::vector<int> result{state.player().position().current.x,state.player().position().current.y,shots.time,shots.reimu_cycle,shots.laser.time,state.invincibility()};
                for(const auto& e:shots.entities) { result.push_back(e.flag);result.push_back(e.age);result.push_back(e.position.current.x);result.push_back(e.position.current.y); }
                return result;
            };
            for(unsigned tick=0;tick<45000;++tick) {
                const auto before=scene.main_state().frames();const auto random=scene.main_state().random_cursor();
                const auto actors=actor_stamp();const bool blocked=scene.dialog_active(),post=scene.post_dialog();
                const bool shoot=scene.resource_stage()==0 || !scene.main_state().kurumi_active() || shooting;
                scene.advance(blocked ? (scene.dialog_status()==dialog::Status::press ? 0x1000 : 0) : (shoot ? shot::input_shot : 0),false,false);
                const auto& state=scene.main_state();
                if(scene.resource_stage()!=1) continue;
                if(blocked && scene.dialog_active()) {
                    require_view(state.frames()==before && state.random_cursor()==random && actor_stamp()==actors,"Kurumi dialog changed game actors/clock/RNG");++frozen;
                }
                if(blocked && post && !scene.dialog_active()) require_view(actor_stamp()==actors,"Kurumi post-dialog repeated actor prefix");
                if(!state.kurumi_active()) continue;
                const auto& boss=state.boss_snapshot();
                if(state.frames()!=before) for(const auto& e:state.orange_events()) {
                    if(e.type==orange::EventType::stage_bonus) ++bonuses;
                    if(e.type==orange::EventType::fade) { ++fades;require_view(boss.phase_frame==417 && state.overlay().time==71,"Kurumi fade did not start at416"); }
                    if(e.type==orange::EventType::next_stage) { ++next;require_view(boss.phase_frame==489,"Kurumi departure did not complete frame488"); }
                }
                bool rays=false;for(const auto& ray:state.kurumi()->snapshot().rays) rays|=ray.flag!=0;
                if(rays) ++ray_frames;
                int checkpoint=-1;
                if(!seen[0] && boss.phase==0) checkpoint=0;
                else if(!seen[1] && boss.phase==1 && boss.phase_frame==16) checkpoint=1;
                else if(!seen[2] && boss.phase==2) checkpoint=2;
                else if(!seen[3] && (rays || (shooting && boss.phase==3))) checkpoint=3;
                else if(!seen[4] && (boss.phase==254 || boss.phase==255)) checkpoint=4;
                else if(!seen[5] && scene.dialog_active() && scene.post_dialog() && scene.dialog_status()==dialog::Status::release) checkpoint=5;
                else if(!seen[6] && scene.post_dialog_complete()) { checkpoint=6;clear_frame=state.frames(); }
                else if(!seen[7] && scene.post_dialog_complete() && boss.phase_frame==417) checkpoint=7;
                else if(!seen[8] && state.next_stage_requested()) checkpoint=8;
                if(checkpoint>=0) {
                    seen[unsigned(checkpoint)]=true;scene.repaint();
                    const auto name=std::string(lunatic ? "lunatic-" : "normal-")+(character ? "marisa-" : "reimu-")+(shooting ? "shot-" : "idle-")+std::to_string(checkpoint);
                    const auto path=kurumi_screenshots+"/"+name+".bmp";write_bmp(path,scene.frame());
                    std::cout<<"MAIN Kurumi fixture="<<name<<" frame="<<state.frames()<<" phase="<<+boss.phase<<" clock="<<boss.phase_frame<<" offset="<<scene.dialog_offset()<<" hp="<<boss.hp<<" pending="<<state.score().score_delta<<" ring="<<state.random_cursor()<<" screenshot="<<path<<'\n';
                }
                if(state.next_stage_requested()) break;
            }
            for(bool capture:seen) require_view(capture,"natural Kurumi fixture missed a progression checkpoint");
            const auto& state=scene.main_state();
            require_view(bonuses==1 && fades==1 && next==1 && frozen>100,"Kurumi dialog/departure consumers differ");
            require_view(shooting || ray_frames>100,"Kurumi timeout did not exercise spawnrays");
            require_view(state.frames()-clear_frame==488 && scene.resident().stage==2 && scene.resident().stage_ascii=='2' && scene.resident().resource_stage==1,"Kurumi departure/resident stage differs");
            require_view(scene.generation()==generation && state.clear_bonus(),"Kurumi clear restarted MAIN or omitted bonus");
            require_view(state.overlay().callback==th04::portable::transition::Callback::none && !state.bonus_text_visible(),"Kurumi final leave retained bonus text");
            const auto actors=actor_stamp();const auto random=state.random_cursor();const auto pending=state.score().score_delta;
            const auto process=scene.process_random_state(),stopped=state.frames();
            for(unsigned i=0;i<3;++i) scene.advance(shot::input_shot|player::left,false,false);
            require_view(state.frames()==stopped && actor_stamp()==actors && state.random_cursor()==random && state.score().score_delta==pending && scene.process_random_state()==process,"pending Stage3 request repeated simulation");
            std::cout<<"MAIN Kurumi stopped character="<<character<<" rank="<<(lunatic ? "Lunatic" : "Normal")<<" shooting="<<shooting<<" frames="<<stopped<<" frozen_ticks="<<frozen<<" ray_frames="<<ray_frames<<" generation="<<generation<<" departure_frames="<<stopped-clear_frame<<" awarded="<<state.clear_bonus()->awarded<<" pending="<<pending<<" progression=stage3_resources_pending\n";
        }
    }
    if (!stage3_screenshots.empty()) {
        for(unsigned lunatic=0;lunatic<2;++lunatic) for(unsigned character=0;character<2;++character) for(unsigned shooting=0;shooting<2;++shooting) {
            FrontEnd scene(background,numerals,labels,cursors,selection_background,portraits,&main_assets);
            scene.enable_stage3();
            if(lunatic) {
                for(unsigned i=0;i<3;++i) scene.input(menu::Input::down);
                scene.input(menu::Input::confirm);scene.input(menu::Input::right);scene.input(menu::Input::right);
                scene.input(menu::Input::cancel);for(unsigned i=0;i<3;++i) scene.input(menu::Input::up);
            }
            scene.input(menu::Input::confirm);if(character) scene.input(menu::Input::right);
            scene.input(menu::Input::confirm);scene.input(menu::Input::confirm);
            std::array<bool,9> seen{};unsigned frozen=0,loads=0,draws=0;bool activated=false;
            const auto generation=scene.generation();
            const auto actor_stamp=[&]() {
                const auto& state=scene.main_state();const auto& shots=state.shots().snapshot();
                std::vector<int> result{state.player().position().current.x,state.player().position().current.y,shots.time,shots.reimu_cycle,shots.laser.time,state.invincibility()};
                for(const auto& e:shots.entities) { result.push_back(e.flag);result.push_back(e.age);result.push_back(e.position.current.x);result.push_back(e.position.current.y); }
                return result;
            };
            for(unsigned tick=0;tick<60000 && !scene.stage3_dialog_complete();++tick) {
                const auto resource=scene.resource_stage();const auto before=scene.main_state().frames();
                const auto random=scene.main_state().random_cursor();const auto actors=actor_stamp();
                const auto process=scene.process_random_state();const bool blocked=scene.dialog_active();
                const bool shoot=resource<2 || shooting;
                scene.advance(blocked ? (scene.dialog_status()==dialog::Status::press ? 0x1000 : 0) : (shoot ? shot::input_shot : 0),false,false);
                const auto& state=scene.main_state();
                if(scene.resource_stage()!=2) continue;
                if(resource==1) {
                    require_view(scene.stage3_resources_valid(),"Stage3 retained preceding sprite bank");
                    ++loads;th04::portable::rng::Lcg32 expected(process);for(unsigned i=0;i<353;++i) expected.next_byte();
                    require_view(scene.process_random_state()==expected.state() && scene.generation()==generation && state.invincibility()==63,"Stage3 changed MAIN generation/RNG or reset invincibility incorrectly");
                }
                if(blocked && (scene.dialog_active() || scene.stage3_dialog_complete())) {
                    require_view(state.frames()==before && state.random_cursor()==random && actor_stamp()==actors,"Stage3 dialog changed actors/clock/RNG");++frozen;
                }
                const auto& boss=state.midboss_state();if(boss.active) { activated=true;draws+=static_cast<unsigned>(state.midboss_draws().size()); }
                int checkpoint=-1;
                if(!seen[0] && state.frames()==1) checkpoint=0;
                else if(!seen[1] && state.frames()==80) checkpoint=1;
                else if(!seen[2] && boss.active && boss.phase==0 && boss.phase_frame==12) checkpoint=2;
                else if(!seen[3] && boss.active && boss.phase==1 && boss.phase_frame==8) checkpoint=3;
                else if(!seen[4] && boss.active && ((shooting && boss.phase==254 && boss.phase_frame==8) || (!shooting && boss.phase==1 && boss.sprite==1 && boss.phase_frame==16))) checkpoint=4;
                else if(!seen[5] && activated && !boss.active) checkpoint=5;
                else if(!seen[6] && scene.dialog_active() && scene.dialog_status()==dialog::Status::release) checkpoint=6;
                else if(!seen[7] && scene.dialog_active() && scene.dialog_status()==dialog::Status::release && scene.boss_portrait_visible()) checkpoint=7;
                else if(!seen[8] && scene.stage3_dialog_complete()) checkpoint=8;
                if(checkpoint>=0) {
                    seen[unsigned(checkpoint)]=true;scene.repaint();
                    if(checkpoint>=7) require_view(scene.stage3_battle_resources_valid(),"Stage3 dialog did not install its eighteen battle slots");
                    const auto name=std::string(lunatic ? "lunatic-" : "normal-")+(character ? "marisa-" : "reimu-")+(shooting ? "shot-" : "idle-")+std::to_string(checkpoint);
                    const auto path=stage3_screenshots+"/"+name+".bmp";write_bmp(path,scene.frame());
                    std::cout<<"MAIN Stage3 fixture="<<name<<" frame="<<state.frames()<<" phase="<<+boss.phase<<" clock="<<boss.phase_frame<<" hp="<<boss.hp<<" offset="<<scene.dialog_offset()<<" power="<<+state.score().power<<" pending="<<state.score().score_delta<<" rng="<<scene.process_random_state()<<" screenshot="<<path<<'\n';
                }
            }
            for(bool capture:seen) require_view(capture,"natural Stage3 fixture missed progression");
            require_view(loads==1 && draws>100 && frozen>100,"Stage3 reset/midboss/dialog missing");
            const auto& state=scene.main_state();const auto frames=state.frames(),process=scene.process_random_state();
            const auto actors=actor_stamp();const auto random=state.random_cursor();const auto offset=scene.dialog_offset();
            for(unsigned i=0;i<3;++i) scene.advance(shot::input_shot|player::left,false,false);
            require_view(state.frames()==frames && actor_stamp()==actors && state.random_cursor()==random && scene.dialog_offset()==offset && scene.process_random_state()==process && !state.boss_active(),"unported Elly frontier advanced gameplay");
            require_view(scene.resident().stage==2 && scene.resident().resource_stage==2 && scene.generation()==generation,"Stage3 resident/resource identity differs");
            std::cout<<"MAIN Stage3 stopped character="<<character<<" rank="<<(lunatic ? "Lunatic" : "Normal")<<" shooting="<<shooting<<" frames="<<frames<<" frozen_ticks="<<frozen<<" loads="<<loads<<" midboss_draws="<<draws<<" generation="<<generation<<" progression=elly_battle_pending\n";
        }
    }
    if (!elly_screenshots.empty()) {
        for(unsigned lunatic=0;lunatic<2;++lunatic) for(unsigned character=0;character<2;++character) for(unsigned shooting=0;shooting<2;++shooting) {
            FrontEnd scene(background,numerals,labels,cursors,selection_background,portraits,&main_assets);
            scene.enable_elly();
            if(lunatic) {
                for(unsigned i=0;i<3;++i) scene.input(menu::Input::down);
                scene.input(menu::Input::confirm);scene.input(menu::Input::right);scene.input(menu::Input::right);
                scene.input(menu::Input::cancel);for(unsigned i=0;i<3;++i) scene.input(menu::Input::up);
            }
            scene.input(menu::Input::confirm);if(character) scene.input(menu::Input::right);
            scene.input(menu::Input::confirm);scene.input(menu::Input::confirm);
            std::array<bool,12> seen{};unsigned frozen=0,bonuses=0,fades=0,next=0,ray_frames=0;
            std::uint32_t clear_frame=0;
            const auto generation=scene.generation();
            const auto actor_stamp=[&]() {
                const auto& state=scene.main_state();const auto& shots=state.shots().snapshot();
                std::vector<int> result{state.player().position().current.x,state.player().position().current.y,shots.time,shots.reimu_cycle,shots.laser.time,state.invincibility()};
                for(const auto& e:shots.entities) { result.push_back(e.flag);result.push_back(e.age);result.push_back(e.position.current.x);result.push_back(e.position.current.y); }
                return result;
            };
            for(unsigned tick=0;tick<65000;++tick) {
                const auto before=scene.main_state().frames();const auto random=scene.main_state().random_cursor();
                const auto actors=actor_stamp();const bool blocked=scene.dialog_active(),post=scene.post_dialog();
                const bool shoot=scene.resource_stage()<2 || !scene.main_state().elly_active() || shooting;
                scene.advance(blocked ? (scene.dialog_status()==dialog::Status::press ? 0x1000 : 0) : (shoot ? shot::input_shot : 0),false,false);
                const auto& state=scene.main_state();
                if(scene.resource_stage()!=2) continue;
                if(blocked && scene.dialog_active()) {
                    require_view(state.frames()==before && state.random_cursor()==random && actor_stamp()==actors,"Elly dialog changed game actors/clock/RNG");++frozen;
                }
                if(blocked && post && !scene.dialog_active()) require_view(actor_stamp()==actors,"Elly post-dialog repeated actor prefix");
                if(!state.elly_active()) continue;
                const auto& boss=state.boss_snapshot();
                if(state.frames()!=before) for(const auto& e:state.orange_events()) {
                    if(e.type==orange::EventType::stage_bonus) ++bonuses;
                    if(e.type==orange::EventType::fade) { ++fades;require_view(boss.phase_frame==417 && state.overlay().time==71,"Elly fade did not start at416"); }
                    if(e.type==orange::EventType::next_stage) { ++next;require_view(boss.phase_frame==489,"Elly departure did not complete frame488"); }
                }
                const auto& elly=state.elly()->snapshot();
                if(elly.scythe.flag==1) ++ray_frames;
                int checkpoint=-1;
                if(!seen[0] && boss.phase==1 && boss.phase_frame==0) checkpoint=0;
                else if(!seen[1] && boss.phase==1 && elly.scythe.mode==1 && elly.scythe.frame==16) checkpoint=1;
                else if(!seen[2] && boss.phase==2 && boss.phase_frame==16) checkpoint=2;
                else if(!seen[3] && boss.phase==3 && boss.mode==0 && boss.phase_frame==16) checkpoint=3;
                else if(!seen[4] && boss.phase==3 && elly.scythe.mode==2 && elly.scythe.flag==1) checkpoint=4;
                else if(!seen[5] && boss.phase==3 && elly.pattern_group>=1) checkpoint=5;
                else if(!seen[6] && boss.phase==3 && elly.pattern_group>=2) checkpoint=6;
                else if(!seen[7] && boss.phase==254 && boss.phase_frame==8) checkpoint=7;
                else if(!seen[8] && scene.dialog_active() && scene.post_dialog() && scene.dialog_status()==dialog::Status::release) checkpoint=8;
                else if(!seen[9] && scene.post_dialog_complete()) { checkpoint=9;clear_frame=state.frames(); }
                else if(!seen[10] && scene.post_dialog_complete() && boss.phase_frame==417) checkpoint=10;
                else if(!seen[11] && state.next_stage_requested()) checkpoint=11;
                if(checkpoint>=0) {
                    seen[unsigned(checkpoint)]=true;scene.repaint();
                    const auto name=std::string(lunatic ? "lunatic-" : "normal-")+(character ? "marisa-" : "reimu-")+(shooting ? "shot-" : "idle-")+std::to_string(checkpoint);
                    const auto path=elly_screenshots+"/"+name+".bmp";write_bmp(path,scene.frame());
                    std::cout<<"MAIN Elly fixture="<<name<<" frame="<<state.frames()<<" phase="<<+boss.phase<<" clock="<<boss.phase_frame<<" group="<<+elly.pattern_group<<" scythe="<<+elly.scythe.mode<<" flag="<<+elly.scythe.flag<<" hit="<<+elly.player_hit<<" offset="<<scene.dialog_offset()<<" hp="<<boss.hp<<" pending="<<state.score().score_delta<<" ring="<<state.random_cursor()<<" screenshot="<<path<<'\n';
                }
                if(state.next_stage_requested()) break;
            }
            for(bool capture:seen) require_view(capture,"natural Elly fixture missed a progression checkpoint");
            const auto& state=scene.main_state();
            require_view(bonuses==1 && fades==1 && next==1 && frozen>100,"Elly dialog/departure consumers differ");
            require_view(shooting || ray_frames>100,"Elly timeout did not exercise the scythe");
            require_view(state.frames()-clear_frame==488 && scene.resident().stage==3 && scene.resident().stage_ascii=='3' && scene.resident().resource_stage==2,"Elly departure/resident stage differs");
            require_view(scene.generation()==generation && state.clear_bonus(),"Elly clear restarted MAIN or omitted bonus");
            require_view(state.overlay().callback==th04::portable::transition::Callback::none && !state.bonus_text_visible(),"Elly final leave retained bonus text");
            const auto actors=actor_stamp();const auto random=state.random_cursor();const auto pending=state.score().score_delta;
            const auto process=scene.process_random_state(),stopped=state.frames();
            for(unsigned i=0;i<3;++i) scene.advance(shot::input_shot|player::left,false,false);
            require_view(state.frames()==stopped && actor_stamp()==actors && state.random_cursor()==random && state.score().score_delta==pending && scene.process_random_state()==process,"pending Stage4 request repeated simulation");
            std::cout<<"MAIN Elly stopped character="<<character<<" rank="<<(lunatic ? "Lunatic" : "Normal")<<" shooting="<<shooting<<" frames="<<stopped<<" frozen_ticks="<<frozen<<" ray_frames="<<ray_frames<<" generation="<<generation<<" departure_frames="<<stopped-clear_frame<<" awarded="<<state.clear_bonus()->awarded<<" pending="<<pending<<" progression=stage4_resources_pending\n";
        }
    }
    if (!stage4_screenshots.empty()) {
        for(unsigned lunatic=0;lunatic<2;++lunatic) for(unsigned character=0;character<2;++character) for(unsigned shooting=0;shooting<2;++shooting) {
            FrontEnd scene(background,numerals,labels,cursors,selection_background,portraits,&main_assets);
            scene.enable_stage4();
            if(lunatic) {
                for(unsigned i=0;i<3;++i) scene.input(menu::Input::down);
                scene.input(menu::Input::confirm);scene.input(menu::Input::right);scene.input(menu::Input::right);
                scene.input(menu::Input::cancel);for(unsigned i=0;i<3;++i) scene.input(menu::Input::up);
            }
            scene.input(menu::Input::confirm);if(character) scene.input(menu::Input::right);
            scene.input(menu::Input::confirm);scene.input(menu::Input::confirm);
            std::array<bool,12> seen{};unsigned activations=0,awards=0,frozen=0,loads=0;
            const auto generation=scene.generation();
            for(unsigned tick=0;tick<85000 && !scene.stage4_dialog_complete();++tick) {
                const auto before=scene.main_state().frames();const auto random=scene.main_state().random_cursor();
                const auto process=scene.process_random_state();const bool blocked=scene.dialog_active();
                const auto previous=scene.main_state().midboss_state();
                std::uint16_t held=blocked ? (scene.dialog_status()==dialog::Status::press ? 0x1000 : 0) : shot::input_shot;
                if(!blocked && scene.resource_stage()==3) {
                    held=shooting ? shot::input_shot : 0;
                    // Recorded player inputs follow the actor; no injected hit,
                    // phase change, spawn or score enters these natural routes.
                    if(shooting && previous.active) {
                        const int dx=previous.position.current.x-scene.main_state().player().position().current.x;
                        if(dx>64) held|=player::right;else if(dx<-64) held|=player::left;
                    }
                }
                scene.advance(held,false,false);
                const auto& state=scene.main_state();if(scene.resource_stage()!=3) continue;
                const auto& actor=state.midboss_state();
                if(state.frames()==1 && !seen[0]) { ++loads;require_view(scene.stage4_resources_valid(),"Stage4 sprite/portrait bank invalid"); }
                if(!previous.active && actor.active) ++activations;
                if(state.frames()!=before) for(const auto& e:state.midboss_events()) if(e.type==th04::portable::midboss::EventType::item) {
                    require_view(e.value==(awards==0 ? 4u : 5u),"Stage4 encounter reward ordering");++awards;
                }
                if(blocked && scene.dialog_active()) {
                    require_view(state.frames()==before && state.random_cursor()==random && scene.process_random_state()==process,"Stage4 dialog advanced simulation/RNG");++frozen;
                }
                int checkpoint=-1;
                const bool first=actor.start_frame==2800;
                if(!seen[0] && state.frames()==1) checkpoint=0;
                else if(!seen[1] && state.frames()==1730) { require_view(!scene.carpet_active(),"carpet callback remained active after lighting");checkpoint=1; }
                else if(!seen[2] && first && actor.active && actor.phase==0 && actor.phase_frame==24) checkpoint=2;
                else if(!seen[3] && first && actor.active && actor.phase==1 && actor.phase_frame==16) checkpoint=3;
                else if(!seen[4] && first && actor.active && ((shooting && actor.phase==254 && actor.phase_frame==8) || (!shooting && actor.phase==1 && actor.phase_frame==128))) checkpoint=4;
                else if(!seen[5] && !first && !actor.active && actor.hp==1200) checkpoint=5;
                else if(!seen[6] && !first && actor.active && actor.phase==0 && actor.phase_frame==24) checkpoint=6;
                else if(!seen[7] && !first && actor.active && actor.phase==1 && actor.phase_frame==16) checkpoint=7;
                else if(!seen[8] && !first && actor.active && ((shooting && actor.phase==254 && actor.phase_frame==8) || (!shooting && actor.phase==1 && actor.phase_frame==128))) checkpoint=8;
                else if(!seen[9] && activations==2 && !actor.active && actor.hp==0) checkpoint=9;
                else if(!seen[10] && scene.dialog_active() && scene.boss_portrait_visible() && scene.dialog_status()==dialog::Status::release) checkpoint=10;
                else if(!seen[11] && scene.stage4_dialog_complete()) checkpoint=11;
                if(checkpoint>=0) {
                    seen[unsigned(checkpoint)]=true;scene.repaint();
                    if(checkpoint>=10) require_view(scene.stage4_battle_resources_valid(),"Stage4 dialog sprite append failed");
                    const auto name=std::string(lunatic ? "lunatic-" : "normal-")+(character ? "marisa-" : "reimu-")+(shooting ? "shot-" : "idle-")+std::to_string(checkpoint);
                    const auto path=stage4_screenshots+"/"+name+".bmp";write_bmp(path,scene.frame());
                    std::cout<<"MAIN Stage4 fixture="<<name<<" frame="<<state.frames()<<" start="<<actor.start_frame<<" active="<<actor.active<<" phase="<<+actor.phase<<" clock="<<actor.phase_frame<<" hp="<<actor.hp<<" ring="<<state.random_cursor()<<" awards="<<awards<<" screenshot="<<path<<'\n';
                }
            }
            for(bool capture:seen) require_view(capture,"natural Stage4 fixture missed a progression checkpoint");
            const auto& state=scene.main_state();require_view(activations==2 && loads==1 && frozen>100,"Stage4 lifecycle/dialog incomplete");
            require_view(shooting ? awards==2 : awards==0,"Stage4 defeat/timeout rewards differ");
            require_view(scene.generation()==generation && scene.resident().stage==3 && scene.resident().resource_stage==3,"Stage4 restarted MAIN or lost resource identity");
            const auto frame=state.frames();const auto random=state.random_cursor();const auto pending=state.score().score_delta;
            for(unsigned i=0;i<3;++i) scene.advance(shot::input_shot|player::left,false,false);
            require_view(state.frames()==frame && state.random_cursor()==random && state.score().score_delta==pending,"Stage4 frontier repeated simulation");
            std::cout<<"MAIN Stage4 stopped character="<<character<<" rank="<<(lunatic ? "Lunatic" : "Normal")<<" shooting="<<shooting<<" frames="<<frame<<" activations="<<activations<<" awards="<<awards<<" frozen_ticks="<<frozen<<" generation="<<generation<<" progression=npc_battle_pending\n";
        }
    }
    if(!reimu_screenshots.empty()) {
        for(unsigned lunatic=0;lunatic<2;++lunatic) for(unsigned shot_type=0;shot_type<2;++shot_type) for(unsigned shooting=0;shooting<2;++shooting) {
            FrontEnd scene(background,numerals,labels,cursors,selection_background,portraits,&main_assets);
            scene.enable_reimu();
            if(lunatic) {
                for(unsigned i=0;i<3;++i) scene.input(menu::Input::down);
                scene.input(menu::Input::confirm);scene.input(menu::Input::right);scene.input(menu::Input::right);
                scene.input(menu::Input::cancel);for(unsigned i=0;i<3;++i) scene.input(menu::Input::up);
            }
            scene.input(menu::Input::confirm);scene.input(menu::Input::right);scene.input(menu::Input::confirm);
            if(shot_type) scene.input(menu::Input::right);
            scene.input(menu::Input::confirm);
            const auto generation=scene.generation();std::array<bool,18> seen{};unsigned frozen=0,bonus=0,fades=0,next=0,orb_checks=0;
            for(unsigned tick=0;tick<150000;++tick) {
                const auto before=scene.main_state().frames();const auto random=scene.main_state().random_cursor();
                const auto process=scene.process_random_state();const bool blocked=scene.dialog_active();
                std::uint16_t held=blocked ? (scene.dialog_status()==dialog::Status::press ? 0x1000 : 0) : shot::input_shot;
                if(!blocked && scene.resource_stage()==3) {
                    held=shooting ? shot::input_shot : 0;
                    if(shooting && scene.main_state().boss_active()) {
                        const int dx=scene.main_state().boss_snapshot().position.current.x-scene.main_state().player().position().current.x;
                        if(dx>64) held|=player::right;else if(dx<-64) held|=player::left;
                    }
                }
                scene.advance(held,false,false);const auto& state=scene.main_state();
                if(scene.resource_stage()!=3 || !state.reimu_active()) continue;
                require_view(scene.stage4_battle_resources_valid(),"Reimu battle resources lost");
                const auto& npc=state.reimu()->snapshot();const auto& boss=npc.boss;
                if(blocked && scene.dialog_active()) {
                    require_view(state.frames()==before && state.random_cursor()==random && scene.process_random_state()==process,"Reimu dialog advanced simulation/RNG");++frozen;
                }
                if(state.frames()!=before) for(const auto& e:state.orange_events()) {
                    if(e.type==orange::EventType::stage_bonus) ++bonus;
                    if(e.type==orange::EventType::fade) { ++fades;require_view(boss.phase_frame==417,"Reimu fade did not start at416"); }
                    if(e.type==orange::EventType::next_stage) { ++next;require_view(boss.phase_frame==489,"Reimu departure did not complete frame488"); }
                    if(e.type==orange::EventType::hit && e.value==192 && e.count==192) ++orb_checks;
                }
                int checkpoint=-1;
                if(boss.phase<=12 && !seen[boss.phase]) checkpoint=boss.phase;
                else if(!seen[13] && boss.phase==254 && boss.phase_frame==8) checkpoint=13;
                else if(!seen[14] && scene.post_dialog() && scene.dialog_active() && scene.boss_portrait_visible() && scene.dialog_status()==dialog::Status::release) checkpoint=14;
                else if(!seen[15] && state.clear_bonus() && state.bonus_text_visible()) checkpoint=15;
                else if(!seen[16] && scene.post_dialog_complete() && boss.phase_frame==417) checkpoint=16;
                else if(!seen[17] && state.next_stage_requested()) checkpoint=17;
                if(checkpoint>=0) {
                    seen[unsigned(checkpoint)]=true;scene.repaint();
                    const auto name=std::string(lunatic ? "lunatic-" : "normal-")+(shot_type ? "b-" : "a-")+(shooting ? "shot-" : "idle-")+std::to_string(checkpoint);
                    const auto path=reimu_screenshots+"/"+name+".bmp";write_bmp(path,scene.frame());
                    unsigned orbs=0;for(const auto& q:npc.orbs) orbs+=q.flag!=0;
                    std::cout<<"MAIN Reimu fixture="<<name<<" frame="<<state.frames()<<" phase="<<+boss.phase<<" clock="<<boss.phase_frame<<" hp="<<boss.hp<<" orbs="<<orbs<<" pending="<<state.score().score_delta<<" ring="<<state.random_cursor()<<" screenshot="<<path<<'\n';
                }
                if(state.next_stage_requested()) break;
            }
            const auto& state=scene.main_state();
            for(unsigned i:{0u,1u,2u,13u,14u,15u,16u,17u}) require_view(seen[i],"natural Reimu route missed a required checkpoint");
            if(!shooting) for(unsigned i=0;i<=12;++i) require_view(seen[i],"idle Reimu route skipped an attack phase");
            require_view(bonus==1 && fades==1 && next==1 && frozen>100 && scene.post_dialog_complete(),"Reimu clear/dialog/departure lifecycle incomplete");
            require_view(scene.generation()==generation && scene.resident().stage==4 && scene.resident().resource_stage==3,"Reimu departure lost MAIN or resource identity");
            const auto frame=state.frames();const auto random=state.random_cursor();const auto pending=state.score().score_delta;
            for(unsigned i=0;i<3;++i) scene.advance(shot::input_shot|player::left,false,false);
            require_view(state.frames()==frame && state.random_cursor()==random && state.score().score_delta==pending,"Stage5 frontier repeated simulation");
            std::cout<<"MAIN Reimu stopped rank="<<(lunatic ? "Lunatic" : "Normal")<<" shot_type="<<shot_type<<" shooting="<<shooting<<" frames="<<frame<<" frozen_ticks="<<frozen<<" orb_checks="<<orb_checks<<" generation="<<generation<<" progression=stage5_pending\n";
        }
    }
    if(!marisa_screenshots.empty()) {
        for(unsigned lunatic=0;lunatic<2;++lunatic) for(unsigned shot_type=0;shot_type<2;++shot_type) for(unsigned shooting=0;shooting<2;++shooting) {
            FrontEnd scene(background,numerals,labels,cursors,selection_background,portraits,&main_assets);
            scene.enable_marisa();
            if(lunatic) {
                for(unsigned i=0;i<3;++i) scene.input(menu::Input::down);
                scene.input(menu::Input::confirm);scene.input(menu::Input::right);scene.input(menu::Input::right);
                scene.input(menu::Input::cancel);for(unsigned i=0;i<3;++i) scene.input(menu::Input::up);
            }
            scene.input(menu::Input::confirm);scene.input(menu::Input::confirm);
            if(shot_type) scene.input(menu::Input::right);
            scene.input(menu::Input::confirm);
            const auto generation=scene.generation();std::array<bool,21> seen{};unsigned frozen=0,bonus=0,fades=0,next=0,bit_checks=0;
            for(unsigned tick=0;tick<150000;++tick) {
                const auto before=scene.main_state().frames();const auto random=scene.main_state().random_cursor();
                const auto process=scene.process_random_state();const bool blocked=scene.dialog_active();
                std::uint16_t held=blocked ? (scene.dialog_status()==dialog::Status::press ? 0x1000 : 0) : shot::input_shot;
                if(!blocked && scene.resource_stage()==3) {
                    held=shooting ? shot::input_shot : 0;
                    if(shooting && scene.main_state().boss_active()) {
                        const int dx=scene.main_state().boss_snapshot().position.current.x-scene.main_state().player().position().current.x;
                        if(dx>64) held|=player::right;else if(dx<-64) held|=player::left;
                    }
                }
                scene.advance(held,false,false);const auto& state=scene.main_state();
                if(scene.resource_stage()!=3 || !state.marisa_active()) continue;
                require_view(scene.stage4_battle_resources_valid(),"Marisa battle resources lost");
                const auto& npc=state.marisa()->snapshot();const auto& boss=npc.boss;
                if(blocked && scene.dialog_active()) {
                    require_view(state.frames()==before && state.random_cursor()==random && scene.process_random_state()==process,"Marisa dialog advanced simulation/RNG");++frozen;
                }
                if(state.frames()!=before) for(const auto& e:state.orange_events()) {
                    if(e.type==orange::EventType::stage_bonus) ++bonus;
                    if(e.type==orange::EventType::fade) { ++fades;require_view(boss.phase_frame==417,"Marisa fade did not start at416"); }
                    if(e.type==orange::EventType::next_stage) { ++next;require_view(boss.phase_frame==489,"Marisa departure did not complete frame488"); }
                    if(e.type==orange::EventType::hit && e.value==192 && e.count==192) ++bit_checks;
                }
                int checkpoint=-1;
                if(boss.phase<=3 && !seen[boss.phase]) checkpoint=boss.phase;
                else if(!seen[4] && boss.phase==254 && boss.phase_frame==8) checkpoint=4;
                else if(!seen[5] && scene.post_dialog() && scene.dialog_active() && scene.boss_portrait_visible() && scene.dialog_status()==dialog::Status::release) checkpoint=5;
                else if(!seen[6] && state.clear_bonus() && state.bonus_text_visible()) checkpoint=6;
                else if(!seen[7] && scene.post_dialog_complete() && boss.phase_frame==417) checkpoint=7;
                else if(!seen[8] && state.next_stage_requested()) checkpoint=8;
                else if(boss.phase==2) {
                    const unsigned attack=boss.mode<=7 ? boss.mode : (boss.mode==10 ? 8 : (boss.mode==11 ? 9 : 10));
                    if(attack<10 && !seen[9+attack]) checkpoint=int(9+attack);
                    else if(npc.alive==4 && !seen[19]) checkpoint=19;
                    else if(npc.alive==0 && !seen[20]) checkpoint=20;
                }
                if(checkpoint>=0) {
                    seen[unsigned(checkpoint)]=true;scene.repaint();
                    const auto name=std::string(lunatic ? "lunatic-" : "normal-")+(shot_type ? "b-" : "a-")+(shooting ? "shot-" : "idle-")+std::to_string(checkpoint);
                    const auto path=marisa_screenshots+"/"+name+".bmp";write_bmp(path,scene.frame());
                    unsigned bits=0;for(const auto& q:npc.bits) bits+=q.flag!=0;
                    std::cout<<"MAIN Marisa fixture="<<name<<" frame="<<state.frames()<<" phase="<<+boss.phase<<" clock="<<boss.phase_frame<<" hp="<<boss.hp<<" mode="<<+boss.mode<<" alive="<<+npc.alive<<" bits="<<bits<<" pending="<<state.score().score_delta<<" ring="<<state.random_cursor()<<" screenshot="<<path<<'\n';
                }
                if(state.next_stage_requested()) break;
            }
            const auto& state=scene.main_state();
            for(unsigned i:{0u,1u,2u,3u,4u,5u,6u,7u,8u}) require_view(seen[i],"natural Marisa route missed a required checkpoint");
            if(!shooting) require_view(seen[19] && seen[20],"idle Marisa route missed bit ownership transitions");
            require_view(bonus==1 && fades==1 && next==1 && frozen>100 && scene.post_dialog_complete(),"Marisa clear/dialog/departure lifecycle incomplete");
            require_view(scene.generation()==generation && scene.resident().stage==4 && scene.resident().resource_stage==3,"Marisa departure lost MAIN or resource identity");
            const auto frame=state.frames();const auto random=state.random_cursor();const auto pending=state.score().score_delta;
            for(unsigned i=0;i<3;++i) scene.advance(shot::input_shot|player::left,false,false);
            require_view(state.frames()==frame && state.random_cursor()==random && state.score().score_delta==pending,"Stage5 frontier repeated simulation");
            std::cout<<"MAIN Marisa stopped rank="<<(lunatic ? "Lunatic" : "Normal")<<" shot_type="<<shot_type<<" shooting="<<shooting<<" frames="<<frame<<" frozen_ticks="<<frozen<<" bit_checks="<<bit_checks<<" generation="<<generation<<" progression=stage5_pending\n";
        }
    }
    if (window) {
        show_window(
            background, numerals, labels, cursors,
            selection_background, portraits, main_assets
        );
    }
}

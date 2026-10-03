#include "view.hpp"
#include "menu_state.hpp"

#include <algorithm>
#include <cstddef>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <utility>

#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#else
#include <SDL.h>
#endif

namespace {

namespace menu = th04::portable::menu;

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

#ifdef _WIN32

struct Win32Title {
    const PiImage& background;
    const CdgSheet& numerals;
    const CdgSheet& labels;
    const CdgSheet& cursors;
    menu::State state;
    Frame frame;

    Win32Title(
        const PiImage& background_, const CdgSheet& numerals_,
        const CdgSheet& labels_, const CdgSheet& cursors_
    ) : background(background_), numerals(numerals_), labels(labels_),
        cursors(cursors_), frame(render_menu(
            background, numerals, labels, cursors, state
        )) {}

    bool input(menu::Input pressed) {
        const menu::Result result = state.handle(pressed);
        if (result.kind == menu::ResultKind::choose_main) {
            std::cout << "title selection=" << unsigned(result.choice)
                      << " (not ported yet)" << std::endl;
        }
        frame = render_menu(background, numerals, labels, cursors, state);
        return result.kind == menu::ResultKind::quit;
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
    case WM_KEYDOWN: {
        if (!title) break;
        bool handled = true;
        bool close = false;
        if (wparam == VK_UP) title->input(menu::Input::up);
        else if (wparam == VK_DOWN) title->input(menu::Input::down);
        else if (wparam == VK_LEFT) title->input(menu::Input::left);
        else if (wparam == VK_RIGHT) title->input(menu::Input::right);
        else if (wparam == VK_RETURN) close = title->input(menu::Input::confirm);
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
            info.bmiHeader.biWidth = LONG(title->frame.width);
            info.bmiHeader.biHeight = -LONG(title->frame.height);
            info.bmiHeader.biPlanes = 1;
            info.bmiHeader.biBitCount = 32;
            info.bmiHeader.biCompression = BI_RGB;
            SetStretchBltMode(dc, COLORONCOLOR);
            StretchDIBits(
                dc, 0, 0, client.right, client.bottom,
                0, 0, int(title->frame.width), int(title->frame.height),
                title->frame.pixels.data(), &info, DIB_RGB_COLORS, SRCCOPY
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
    const CdgSheet& labels, const CdgSheet& cursors
) {
    Win32Title title(background, numerals, labels, cursors);
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
    MSG message{};
    while (GetMessageW(&message, nullptr, 0, 0) > 0) {
        TranslateMessage(&message);
        DispatchMessageW(&message);
    }
}

#else

void show_window(
    const PiImage& background, const CdgSheet& numerals,
    const CdgSheet& labels, const CdgSheet& cursors
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

    menu::State state;
    bool running = true;
    bool dirty = true;
    Frame frame;
    while (running) {
        SDL_Event event{};
        if (!dirty && SDL_WaitEvent(&event)) {
            SDL_PushEvent(&event);
        }
        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_QUIT) running = false;
            if (event.type != SDL_KEYDOWN || event.key.repeat) continue;
            switch (event.key.keysym.sym) {
            case SDLK_UP:
                state.handle(menu::Input::up);
                dirty = true;
                break;
            case SDLK_DOWN:
                state.handle(menu::Input::down);
                dirty = true;
                break;
            case SDLK_LEFT:
                state.handle(menu::Input::left);
                dirty = true;
                break;
            case SDLK_RIGHT:
                state.handle(menu::Input::right);
                dirty = true;
                break;
            case SDLK_RETURN:
            case SDLK_KP_ENTER:
                {
                    const menu::Result result = state.handle(menu::Input::confirm);
                    if (result.kind == menu::ResultKind::choose_main) {
                        std::cout << "title selection=" << unsigned(result.choice)
                                  << " (not ported yet)" << std::endl;
                    }
                    if (result.kind == menu::ResultKind::quit) running = false;
                    dirty = true;
                }
                break;
            case SDLK_ESCAPE:
                if (state.handle(menu::Input::cancel).kind == menu::ResultKind::quit) {
                    running = false;
                }
                dirty = true;
                break;
            default:
                break;
            }
        }
        if (!running) break;
        if (dirty) {
            frame = render_menu(background, numerals, labels, cursors, state);
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
    const std::string& screenshot, const std::string& options_screenshot,
    bool window
) {
    const CdgSheet numerals(numeral_bytes);
    const CdgSheet labels(label_bytes);
    const CdgSheet cursors(cursor_bytes);
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
    if (window) {
        show_window(background, numerals, labels, cursors);
    }
}

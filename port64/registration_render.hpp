#pragma once
#include "registration.hpp"
#include "cutscene_scene.hpp"
#include "sprite_sheet.hpp"
#include <memory>

namespace th04::portable::registration {
// PC-98 TRAM has independent WORD character and attribute banks. Retain
// half-cell codes so replacing one gaiji also replaces its two attributes.
// This owner handles the registration gaiji bank, not general console text.
class TextPlane {
public:
    void put(int column,int row,Byte gaiji,std::uint16_t attribute);
    void put_string(int column,int row,const std::string&,std::uint16_t attribute);
    void clear();
    score_file::Bytes bytes() const;
    // RGB overlay values do not follow the analog graphics palette or tone.
    void overlay(score_file::Bytes& rgb,const score_file::Bytes& gaiji,const dialog::Font&) const;
private:
    std::array<std::uint16_t,2000> codes_{},attributes_{};
};
struct GraphicsAssets {
    cutscene::Assets graphics;
    score_file::Bytes numerals;
    unsigned text_weight=0; // Inherited graph_putsa_fx WORD effect (0..3).
    std::string non_turbo_message; // Supplied attested Shift-JIS, never Unicode.
};
// Graphics consumer only: palette waits, keyboard sampling, audio, host file
// persistence and return to OP belong to the scene. Keep page1 as the clean
// HI01 background; edited names restore a WORD-aligned strip into page0.
class Renderer {
public:
    Renderer(const GraphicsAssets&,Byte selected_character,Byte entered_place,
             std::array<score_file::Bytes,2> pages={},unsigned shown=0);
    void apply(const Event&);
    const cutscene::Canvas& canvas() const { return canvas_; }
    const TextPlane& text_plane() const { return text_; }
    score_file::Bytes rgb(unsigned page,int tone=100) const;
    void put_numeral(int left,int top,unsigned pattern);
    void restore_name_background(int left,int top,unsigned width,unsigned height);
private:
    void row(const score_file::Bytes&,unsigned place,Byte character);
    std::string name(const score_file::Bytes&,unsigned place) const;
    const GraphicsAssets* assets_;
    cutscene::Canvas canvas_;
    TextPlane text_;
    dialog::Font font_;
    std::unique_ptr<sprite::Sheet> numerals_;
    Byte selected_character_,entered_place_;
};
} // namespace th04::portable::registration

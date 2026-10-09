#pragma once
#include "gameover.hpp"
#include "registration_render.hpp"

namespace th04::portable::gameover {
// Game Over freezes MAIN graphics while its separate TRAM and palette clock
// advance. Text stays bright over the graphics tone, including reversed spaces.
class Renderer {
public:
    using Bytes=score_file::Bytes;
    Renderer(const Bytes& gaiji,const Bytes& font_bitmap,Bytes indexed,
             std::array<std::uint8_t,48> palette,registration::TextPlane text={});
    void apply(const Event&);
    void update_score(const score::Snapshot&);
    void update_hud(const registration::TextPlane&);
    const Bytes& indexed() const {return indexed_;}
    const std::array<std::uint8_t,48>& palette() const {return palette_;}
    const registration::TextPlane& text() const {return text_;}
    Bytes rgb(int tone) const;
private:
    const Bytes* gaiji_;
    dialog::Font font_;
    Bytes indexed_;
    std::array<std::uint8_t,48> palette_;
    registration::TextPlane text_;
};
} // namespace th04::portable::gameover

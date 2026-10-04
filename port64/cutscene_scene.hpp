#pragma once
#include "cutscene.hpp"
#include "dialog.hpp"
#include "pi_image.hpp"
#include <array>
#include <map>
#include <memory>

namespace th04::portable::cutscene {
struct Assets {
    std::map<std::string,Bytes> scripts;
    std::map<std::string,PiImage> pictures;
    Bytes font_bitmap, gaiji;
};

// Owns both graphics pages, the saved text-box pixels and the currently
// loaded PI slot. It is a graphics owner, so text follows the analog palette
// and is erased with the saved background; MAIN dialogue TRAM is different.
class Scene {
public:
    Scene(const Assets& assets,const std::string& script);
    void advance(std::uint16_t held,const Sink& observer={});
    void apply(const Event& event);
    const Script& script() const { return script_; }
    Script& script() { return script_; }
    const Bytes& page(unsigned page) const { return pages_.at(page); }
    const std::array<std::uint8_t,48>& palette() const { return palette_; }
    unsigned shown_page() const { return shown_; }
    unsigned access_page() const { return accessed_; }
    int scroll() const { return scroll_; }
    std::size_t event_count() const { return event_count_; }
    const std::vector<Event>& pending_sound_requests() const { return sound_requests_; }
    void clear_sound_requests() { sound_requests_.clear(); }
private:
    void rect_copy(unsigned source,unsigned dest,int x,int y,unsigned w,unsigned h,unsigned mask);
    void draw_picture(int x,int y,int quarter,unsigned mask,bool full=false);
    void glyph(const Event& event,bool gaiji);
    const Assets* assets_;
    Script script_;
    dialog::Font font_;
    std::array<Bytes,2> pages_;
    Bytes box_background_;
    const PiImage* loaded_=nullptr;
    std::array<std::uint8_t,48> palette_{};
    unsigned shown_=0,accessed_=0;
    int scroll_=0;
    std::size_t event_count_=0;
    std::vector<Event> sound_requests_;
};
} // namespace th04::portable::cutscene

#include "gameover_render.hpp"
#include <stdexcept>

namespace th04::portable::gameover {
Renderer::Renderer(const Bytes& gaiji,const Bytes& bitmap,Bytes indexed,
                   std::array<std::uint8_t,48> palette,registration::TextPlane text)
    :gaiji_(&gaiji),font_(bitmap),indexed_(std::move(indexed)),palette_(palette),text_(std::move(text)) {
    if(indexed_.size()!=640*400)throw std::invalid_argument("incomplete Game Over graphics");
    for(auto index:indexed_)if(index>15)throw std::invalid_argument("Game Over graphics index outside palette");
}
void Renderer::apply(const Event& e) {
    switch(e.kind) {
    case Kind::gaiji:
        if(e.text.empty())text_.put(e.left,e.row,std::uint8_t(e.value),std::uint16_t(e.attribute));
        else text_.put_string(e.left,e.row,e.text,std::uint16_t(e.attribute));
        break;
    case Kind::ank:
        for(unsigned i=0;i<e.text.size();++i) {
            if(!e.text[i])break;
            const unsigned at=unsigned(e.row*80+e.left)+i;
            text_.put_ank(at%80,at/80,std::uint8_t(e.text[i]),std::uint16_t(e.attribute));
        }
        break;
    case Kind::wipe:case Kind::black:
        for(int row=1;row<24;++row)for(int column=4;column<52;++column)
            text_.put_ank(column,row,32,e.kind==Kind::wipe ? 0xe1 : 5);
        break;
    default:break; // Clocks, HUD/resource publication, sound and save are scene-owned.
    }
}
Renderer::Bytes Renderer::rgb(int tone) const {
    if(tone<0 || tone>200)throw std::invalid_argument("Game Over tone outside native palette range");
    Bytes result(640*400*3);
    for(unsigned at=0;at<indexed_.size();++at)for(unsigned channel=0;channel<3;++channel) {
        const int base=palette_[indexed_[at]*3+channel]>>4;
        const int component=tone<=100 ? base*tone/100 : 15-(15-base)*(200-tone)/100;
        result[at*3+channel]=std::uint8_t(component*17);
    }
    text_.overlay(result,*gaiji_,font_);return result;
}
void Renderer::update_score(const score::Snapshot& snapshot) {
    auto board=snapshot;
    for(const auto& event:score::render(board))
        if(event.kind==score::Kind::gaiji)
            text_.put_string(int(event.left),int(event.row),event.bytes,std::uint16_t(event.value));
}
} // namespace th04::portable::gameover

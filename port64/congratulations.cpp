#include "congratulations.hpp"
#include <stdexcept>

namespace th04::portable::maine {
std::string congratulations_picture(unsigned playchar,unsigned rank) {
    if(playchar>1 || rank>4)throw std::invalid_argument("invalid congratulations character/rank");
    std::string name="CONG00.pi";name[4]=char('0'+playchar);name[5]=char('0'+rank);return name;
}
std::vector<Request> congratulations_requests(unsigned playchar,unsigned rank) {
    using K=RequestKind;
    // Recovered _main selects page1, loads/applies/puts/frees PI slot0, then
    // copies the opposite page to0. It does not clear TRAM or draw a new font.
    return {{K::access,1},{K::pi_load,0,0,0,0,0,congratulations_picture(playchar,rank)},
        {K::pi_palette},{K::pi_put},{K::pi_free},{K::copy_page,0},
        {K::fade,0,1,1},{K::wait,0},{K::fade,0,0,4}};
}
Congratulations::Congratulations(const cutscene::Assets& assets,unsigned playchar,unsigned rank,
                               std::array<Bytes,2> pages,unsigned shown)
    :canvas_(assets,std::move(pages),shown),picture_(congratulations_picture(playchar,rank)),
     animation_(congratulations_requests(playchar,rank)) {}
void Congratulations::advance(std::uint16_t held,const RequestSink& observer) {
    animation_.advance(held,[&](const Request& e) {
        using K=RequestKind;using C=cutscene::Kind;
        switch(e.kind) {
        case K::access:canvas_.apply({C::access,e.a});break;
        case K::pi_load: { cutscene::Event load{C::pi_load};load.name=e.data;canvas_.apply(load);break; }
        case K::pi_palette:canvas_.apply({C::pi_palette});break;
        case K::pi_put:canvas_.apply({C::pi_put,e.a,e.b});break;
        case K::pi_free:canvas_.apply({C::pi_free});break;
        case K::copy_page:canvas_.apply({C::copy_page,e.a});break;
        default:break; // The independent clock owns fades and the keyboard wait.
        }
        if(observer)observer(e);
    });
}
} // namespace th04::portable::maine

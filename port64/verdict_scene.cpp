#include "verdict_scene.hpp"

namespace th04::portable::verdict {
Scene::Scene(const cutscene::Assets& assets,const Input& input,std::array<Bytes,2> pages,unsigned shown)
    :canvas_(assets,std::move(pages),shown),script_(Plan(input,assets.scripts.at("_UDE.TXT"))) {}
void Scene::advance(std::uint16_t keys,const Sink& observer) {
    script_.advance(keys,[&](const Event& e) { apply(e);if(observer)observer(e); });
}
void Scene::apply(const Event& e) {
    using C=cutscene::Kind;
    switch(e.kind) {
    case Kind::text:canvas_.put_text(e.a,e.b,e.data,unsigned(e.c),unsigned(e.d));break;
    case Kind::gaiji:canvas_.put_gaiji(e.a,e.b,e.data,e.c,unsigned(e.d));break;
    case Kind::access:canvas_.apply({C::access,e.a});break;
    case Kind::show:canvas_.apply({C::show,e.a});break;
    case Kind::copy_page:canvas_.apply({C::copy_page,e.a});break;
    case Kind::pi_load: {
        cutscene::Event load{C::pi_load};load.name=e.data;canvas_.apply(load);break;
    }
    case Kind::pi_palette:canvas_.apply({C::pi_palette});break;
    case Kind::pi_put:canvas_.apply({C::pi_put,e.a,e.b});break;
    case Kind::pi_free:canvas_.apply({C::pi_free});break;
    default:break; // Clock and bounded commentary bytes are owned by Script/Plan.
    }
}
} // namespace th04::portable::verdict

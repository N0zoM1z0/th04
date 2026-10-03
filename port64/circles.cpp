#include "circles.hpp"

namespace th04::portable::circle {
bool System::add(motion::Point center,bool growing) {
    for (auto& e:state_.entities) {
        if (e.flag) continue;
        e.flag=1;e.age=0;
        // The circle producer uses signed IDIV, unlike sprite coordinates
        // which use arithmetic SAR. Negative fractions truncate toward zero.
        e.center={motion::wrap(center.x/16+32),motion::wrap(center.y/16+16)};
        e.radius=growing ? 4 : 132;e.delta=growing ? 8 : -8;return true;
    }
    return false;
}
void System::update() {
    for (auto& e:state_.entities) {
        if (e.flag==2) e.flag=0;
        if (e.flag!=1) continue;
        e.radius=motion::wrap(int(e.radius)+e.delta);++e.age;
        if (e.age>16) e.flag=2;
        // Original render requires flag1: age17 is removed before drawing,
        // although the old DOS comment suggests it still draws that frame.
    }
}
std::vector<motion::Point> raster(motion::Point center,std::uint16_t radius) {
    std::vector<motion::Point> result;
    if (!radius) return result;
    int x=motion::wrap(radius),y=0,error=x;
    const int cx=center.x,cy=center.y;
    const auto sub=[](int a,int b) { return int(motion::wrap(a-b)); };
    const auto add=[](int a,int b) { return int(motion::wrap(a+b)); };
    // Preserve the signed-word coarse rejection used before the midpoint
    // loop, including diagnostic negative/overflowing input coordinates.
    if (sub(cy,x)>399 || add(cy,x)<0 || sub(cx,x)>639 || add(cx,x)<0) return result;
    const bool inside=sub(cy,x)>=0 && add(cy,x)<=399 && sub(cx,x)>=0 && add(cx,x)<=639;
    const auto pixel=[&](int px,int py) {
        if (px>=0 && px<=639 && py>=0 && py<=399) result.push_back({static_cast<std::int16_t>(px),static_cast<std::int16_t>(py)});
    };
    const auto four=[&](int dx,int dy) {
        const int top=sub(cy,dy),bottom=add(cy,dy);
        if (inside || dy) {
            pixel(sub(cx,dx),top);pixel(add(cx,dx),top);
        }
        if (inside || bottom<399) {
            pixel(sub(cx,dx),bottom);pixel(add(cx,dx),bottom);
        }
    };
    do {
        four(x,y);if (x!=y || inside) four(y,x);
        error=motion::wrap(error-y-1);error=motion::wrap(error-y);
        if (error<0) { x=motion::wrap(x-1);error=motion::wrap(error+x);error=motion::wrap(error+x); }
        y=motion::wrap(y+1);
    } while (x>=y);
    return result;
}
} // namespace th04::portable::circle

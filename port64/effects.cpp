#include "effects.hpp"
#include <stdexcept>

namespace th04::portable::spark {
namespace {
bool inside(motion::Point p) {
    return static_cast<std::uint16_t>(p.x)<=6144 && static_cast<std::uint16_t>(p.y)<=5888;
}
void start(Entity& e,motion::Point center) { e.flag=1;e.age=0;e.center.current=center; }
}
bool pixel(unsigned cel,unsigned x,unsigned y) {
    if (cel>=8 || x>=8 || y>=8) throw std::out_of_range("spark pixel");
    if (!cel) return (x==3 && y<=3) || (y==3 && x>=3) || (x==4 && y>=4) || (y==4 && x<=4);
    if (cel==1 || cel==4) {
        return (y<3 && x==y+1) || (y>=1 && y<=3 && x+y==8) ||
               (y>=4 && y<=6 && x+y==6) || (y>=5 && x+1==y) ||
               (x>=3 && x<=4 && y>=3 && y<=4);
    }
    if (cel==7) {
        const int dx=2*int(x)-7,dy=2*int(y)-7,d=dx*dx+dy*dy;
        return (d>=50 && d<=58) || d==2;
    }
    const unsigned margin=cel==2 || cel==5 ? 1 : 2;
    return y>=margin && y<8-margin && (x==y || x+y==7);
}
void System::initialize(const std::function<std::uint8_t()>& next_byte) {
    // DOS initializes only these low bytes, preserving the high angle bytes
    // and the high ring-offset byte. Stage clearing normally makes them zero.
    for (auto& e:state_.entities) e.angle=static_cast<std::uint16_t>((e.angle&0xff00u)|next_byte());
    state_.ring_offset&=0xff00u;
}
Entity& System::slot() {
    if (state_.ring_offset>=pool_size*16 || state_.ring_offset%16) {
        throw std::out_of_range("corrupted spark ring offset");
    }
    return state_.entities[state_.ring_offset/16];
}
void System::advance() {
    state_.ring_offset=static_cast<std::uint16_t>(state_.ring_offset+16);
    if (state_.ring_offset>=pool_size*16) state_.ring_offset=0;
}
void System::add_random(motion::Point center,motion::Subpixel radius,std::uint16_t count,
                        randring::SharedRandomRing& random) {
    if (!inside(center)) return;
    // This is a ring of ATTEMPTS: occupied slots still advance the offset,
    // but only free slots consume a random sample. Count zero wraps through
    // 65536 attempts, matching the original word-sized decrement loop.
    do {
        auto& e=slot();
        if (!e.flag) {
            start(e,center);
            const auto length=motion::wrap(std::int32_t(radius)+random.next16_and(31));
            e.center.velocity=motion::polar(static_cast<std::uint8_t>(e.angle),length);
        }
        advance();
    } while (--count);
}
void System::add_circle(motion::Point center,motion::Subpixel radius,std::uint16_t count) {
    if (!inside(center)) return;
    if (!count) throw std::domain_error("zero spark circle divisor");
    // The premultiplied numerator is a WORD. Counts divisible by 256 start
    // at zero and nevertheless execute 256 attempts before returning to zero.
    auto numerator=static_cast<std::uint16_t>(count<<8);
    do {
        auto& e=slot();
        if (!e.flag) {
            start(e,center);
            e.center.velocity=motion::polar(static_cast<std::uint8_t>(numerator/count),radius);
        }
        advance();numerator=static_cast<std::uint16_t>(numerator-256);
    } while (numerator);
}
void System::update() {
    for (auto& e:state_.entities) {
        if (!e.flag) continue;
        if (e.flag!=1) { e.flag=0;continue; }
        e.center.update();
        const auto x=static_cast<std::uint16_t>(std::int32_t(e.center.current.x)+64);
        const auto y=static_cast<std::uint16_t>(std::int32_t(e.center.current.y)+64);
        if (x>=6272 || y>=6016) { e.flag=2;continue; }
        e.center.velocity.y=motion::wrap(std::int32_t(e.center.velocity.y)+1);
        ++e.age;if (e.age>40) e.flag=2;
    }
}
} // namespace th04::portable::spark

namespace th04::portable::gather {
bool pixel(unsigned x,unsigned y) {
    if (x>=8 || y>=8) throw std::out_of_range("gather pixel");
    const int dx=2*int(x)-7,dy=2*int(y)-7;
    return dx*dx+dy*dy<=64;
}
bool System::add(const Template& shape,const bullet::Template& bullet,bool only) {
    state_.scratch=shape;
    for (auto& e:state_.entities) {
        if (e.flag) continue;
        e.flag=1;
        if (only) e.bullet.spawn_type=0;else e.bullet=bullet;
        e.center.current=shape.center;e.center.velocity=shape.velocity;
        e.radius=e.previous_radius=shape.radius;
        e.angle=0;e.angle_delta=shape.angle_delta;e.color=shape.color;e.ring_points=shape.ring_points;
        e.radius_delta=static_cast<motion::Subpixel>(shape.radius/32);
        return true;
    }
    return false;
}
bool System::request(const bullet::Event& event) {
    if (event.type!=bullet::EventType::gather) throw std::invalid_argument("not a gather request");
    Template shape;shape.center=event.bullet.origin;
    return add(shape,event.bullet);
}
void System::update(const std::function<void(const bullet::Template&)>& release) {
    for (auto& e:state_.entities) {
        if (!e.flag) continue;
        if (e.flag>=2) { e.flag=0;continue; }
        e.center.update();e.previous_radius=e.radius;
        e.radius=motion::wrap(std::int32_t(e.radius)-e.radius_delta);
        e.angle=static_cast<std::uint8_t>(e.angle+e.angle_delta);
        if (e.radius<32) {
            e.flag=2;
            if (e.bullet.spawn_type && release) {
                auto saved=e.bullet;saved.origin=e.center.current;release(saved);
            }
        }
    }
}
std::vector<Point> System::points() const {
    std::vector<Point> result;
    for (const auto& e:state_.entities) {
        if (e.flag!=1) continue;
        for (int i=0;i<e.ring_points;++i) {
            // TC4J shifts a signed word before division; large point counts
            // must not silently use the host's wider multiplication.
            const auto angle=static_cast<std::uint8_t>(motion::wrap(i*256)/e.ring_points+e.angle);
            const auto offset=motion::polar(angle,e.radius);
            const motion::Point p{motion::wrap(std::int32_t(e.center.current.x)+offset.x),
                                  motion::wrap(std::int32_t(e.center.current.y)+offset.y)};
            if (p.x>-64 && p.x<6208 && p.y>-64 && p.y<5952) result.push_back({p,e.color});
        }
    }
    return result;
}
} // namespace th04::portable::gather

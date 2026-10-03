#pragma once
#include "enemy_bullets.hpp"

namespace th04::portable::spark {
constexpr unsigned pool_size=96;
struct Entity {
    std::uint8_t flag=0,age=0;
    motion::Motion center{};
    std::uint16_t angle=0;
};
struct Snapshot {
    std::array<Entity,pool_size> entities{};
    std::uint16_t ring_offset=0;
};
// Geometry is generated from lines/disks, without embedded original bitmaps.
bool pixel(unsigned cel,unsigned x,unsigned y);
class System {
public:
    explicit System(Snapshot initial={}):state_(initial) {}
    const Snapshot& snapshot() const { return state_; }
    void initialize(const std::function<std::uint8_t()>& next_byte);
    void add_random(motion::Point center,motion::Subpixel radius,std::uint16_t count,
                    randring::SharedRandomRing& random);
    void add_circle(motion::Point center,motion::Subpixel radius,std::uint16_t count);
    void update();
private:
    Entity& slot();
    void advance();
    Snapshot state_;
};
} // namespace th04::portable::spark

namespace th04::portable::gather {
constexpr unsigned pool_size=16;
struct Template {
    motion::Point center{},velocity{};
    motion::Subpixel radius=1024;
    std::int16_t ring_points=8;
    std::uint8_t color=9,angle_delta=2;
};
struct Entity {
    std::uint8_t flag=0,color=0;
    motion::Motion center{};
    motion::Subpixel radius=0;
    std::int16_t ring_points=0;
    std::uint8_t angle=0,angle_delta=0;
    bullet::Template bullet{};
    motion::Subpixel previous_radius=0,radius_delta=0;
};
struct Snapshot {
    std::array<Entity,pool_size> entities{};
    Template scratch{};
};
struct Point { motion::Point position{};std::uint8_t color=0; };
bool pixel(unsigned x,unsigned y);
class System {
public:
    explicit System(Snapshot initial={}):state_(initial) {}
    const Snapshot& snapshot() const { return state_; }
    Template& scratch() { return state_.scratch; }
    bool add(const Template& shape,const bullet::Template& bullet,bool only=false);
    bool request(const bullet::Event& event);
    void update(const std::function<void(const bullet::Template&)>& release);
    std::vector<Point> points() const;
private:
    Snapshot state_;
};
} // namespace th04::portable::gather

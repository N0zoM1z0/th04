#include "yuuka6.hpp"
#include <stdexcept>

namespace th04::portable::yuuka6 {
namespace {
struct Cel { std::int16_t frame;std::uint8_t sprite; };
// Semantic animation cels, checked against the eight original executable
// helpers. They are loaded sprite-bank indices, not executable byte arrays.
constexpr Cel close_cels[]={{1,128},{7,130},{13,132},{19,134}};
constexpr Cel open_cels[]={{1,134},{7,132},{13,130},{19,128}};
constexpr Cel forward_cels[]={{1,134},{7,136},{13,152},{19,138}};
constexpr Cel left_cels[]={{1,134},{7,136},{13,150}};
constexpr Cel spin_cels[]={{1,150},{4,152},{7,154},{10,156},{13,158},{16,160},
    {19,162},{22,164},{25,166},{28,168},{31,170},{34,172},{37,134}};
constexpr Cel vanish_cels[]={{1,174},{8,176},{15,178},{22,180},{29,0}};
constexpr Cel appear_cels[]={{1,180},{8,178},{15,176},{22,174},{29,128}};
constexpr Cel shield_cels[]={{1,128},{7,142},{13,144}};
struct Sequence { const Cel* cels;unsigned count;std::int16_t end;std::uint8_t flag; };
template<unsigned N> constexpr Sequence sequence(const Cel (&cels)[N],std::int16_t end,std::uint8_t flag) {
    return {cels,N,end,flag};
}
constexpr Sequence animations[]={sequence(close_cels,25,2),sequence(open_cels,25,1),
    sequence(forward_cels,25,3),sequence(left_cels,19,4),sequence(spin_cels,40,2),
    sequence(vanish_cels,36,0),sequence(appear_cels,36,1),sequence(shield_cels,19,8)};
// Initialized MAIN DATA: two five-node paths, angles measured in a full BYTE
// turn. The sixth patterns_seen residue returns through move_towards().
constexpr std::uint8_t fly_angles[2][5]={{0x60,0x00,0x70,0xE0,0x80},
                                       {0x20,0x70,0x90,0xF0,0x10}};
} // namespace

bool System::animate(Animation animation) {
    const auto index=static_cast<unsigned>(animation);
    if(index>=8) throw std::invalid_argument("unknown Yuuka6 animation");
    // Close/open stamp their starting flags on *every* call. All other
    // animations retain the incoming flag until their terminal clock value.
    if(animation==Animation::close) state_.sprite_flag=1;
    if(animation==Animation::open) state_.sprite_flag=2;
    state_.animation_frame=motion::wrap(std::int32_t(state_.animation_frame)+1);
    const auto& sequence=animations[index];
    for(unsigned i=0;i<sequence.count;++i)
        if(state_.animation_frame==sequence.cels[i].frame) state_.boss.sprite=sequence.cels[i].sprite;
    if(state_.animation_frame!=sequence.end) return false;
    state_.animation_frame=0;state_.sprite_flag=sequence.flag;return true;
}

bool System::move_towards(motion::Point destination) {
    auto& b=state_.boss;
    // MAIN13A9:69A9: the destination is used only at clock64. Vanish/appear
    // runs first, even on a completion/teleport frame. Negative clocks take
    // the vanish branch; this is a signed comparison, not a host timer.
    if(b.phase_frame<64) {
        if(state_.sprite_flag!=0) animate(Animation::vanish);
    } else if(state_.sprite_flag==0) animate(Animation::appear);
    if(b.phase_frame==64) {
        b.position.current=destination;
        if(state_.mirror_state!=0) {
            state_.mirror_state=2;
            state_.mirror={motion::wrap(6144-std::int32_t(destination.x)),destination.y};
        }
    } else if(b.phase_frame==128) {
        b.phase_frame=0;++b.patterns_or_bonus;return true;
    }
    return false;
}

bool System::phase2_fly() {
    auto& b=state_.boss;
    const auto node=b.patterns_or_bonus%6u;
    if(node==5) return move_towards({3072,1280});
    if(b.phase_frame==1) {
        // The DOS routine indexes the table unchecked. Native only accepts
        // the two paths selected by randring&1; malformed snapshots cannot
        // silently read adjacent DATA or invent a fallback trajectory.
        if(state_.fly_path>=2) throw std::invalid_argument("invalid Yuuka6 flight path");
        b.position.velocity=motion::polar(fly_angles[state_.fly_path][node],8);
    } else if(b.phase_frame==112) {
        b.phase_frame=0;++b.patterns_or_bonus;return true;
    }
    // No previous-position copy: the target only adds velocity to current.
    b.position.current.x=motion::wrap(std::int32_t(b.position.current.x)+b.position.velocity.x);
    b.position.current.y=motion::wrap(std::int32_t(b.position.current.y)+b.position.velocity.y);
    return false;
}

void System::horizontal_wave() {
    auto& b=state_.boss;
    if(b.phase_frame==1) { b.position.velocity.x=32;b.angle=0; }
    b.position.current.x=motion::wrap(std::int32_t(b.position.current.x)+b.position.velocity.x);
    // Reverse after moving across either inclusive boundary, without clamp.
    if(b.position.current.x<=768 || b.position.current.x>=5376)
        b.position.velocity.x=motion::wrap(-std::int32_t(b.position.velocity.x));
    b.position.current.y=motion::wrap(1280+std::int32_t(motion::polar(b.angle,768).y));
    b.angle=static_cast<std::uint8_t>(b.angle+2u);
}

bool System::move_to_center() {
    auto& b=state_.boss;
    if(state_.sprite_flag==0) { animate(Animation::appear);return false; }
    state_.aux_flag=0;
    // Success is the entire subpixel interval [192,193), not exact equality.
    // In particular, the frame that steps into that interval still returns
    // false. A completed appearance also waits until the following call.
    if(b.position.current.x<3072)
        b.position.current.x=motion::wrap(std::int32_t(b.position.current.x)+16);
    else if(b.position.current.x>=3088)
        b.position.current.x=motion::wrap(std::int32_t(b.position.current.x)-16);
    else return true;
    return false;
}
} // namespace th04::portable::yuuka6

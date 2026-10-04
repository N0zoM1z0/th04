#include "stage6.hpp"
#include <stdexcept>

namespace th04::portable::stage6 {
Setup prepare(orange::Snapshot boss, midboss::Snapshot midboss, unsigned rank) {
    // Extra has its own stagex_setup. The original selector indexes four
    // stack arguments: rank4 reads the far return CS, not a Normal fallback.
    if(rank>=4) throw std::invalid_argument("Stage6 requires an ordinary rank");
    // boss_reset clears the motion/phase scratch and small explosion flags,
    // but retains HP, endHP, angle, big explosion and additional[2..15].
    boss.phase=0; boss.mode=0; boss.patterns_or_bonus=0;
    boss.phase_frame=0; boss.damage=0; boss.position.velocity={};
    boss.small[0].alive=boss.small[1].alive=0; boss.timed_out=1;
    boss.position.current=boss.position.previous={3072,1280};
    boss.sprite=128; boss.hitbox_radius={384,768};
    constexpr std::uint8_t interval[]{48,64,80,96}, count[]{1,1,2,4};
    boss.additional[0]=interval[rank]; boss.additional[1]=count[rank];
    // midboss_reset precedes setup. Its retained motion/phase/sprite storage
    // does not authorize a preceding callback: both callbacks are null.
    midboss.active=false; midboss.hp=0; midboss.start_frame=60000;
    return {boss,midboss};
}
} // namespace th04::portable::stage6

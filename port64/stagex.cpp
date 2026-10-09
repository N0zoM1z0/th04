#include "stagex.hpp"

namespace th04::portable::stagex {
Setup prepare(orange::Snapshot boss,midboss::Snapshot midboss) {
    midboss.active=false;
    midboss.start_frame=5400;
    midboss.position.current=midboss.position.previous={-256,4096};
    midboss.position.velocity={64,-64};
    midboss.hp=4096;midboss.sprite=0;midboss.unused_angle=96;
    boss.phase=0;boss.mode=0;boss.patterns_or_bonus=0;
    boss.phase_frame=0;boss.damage=0;boss.position.velocity={};
    boss.small[0].alive=boss.small[1].alive=0;boss.timed_out=1;
    boss.position.current=boss.position.previous={3072,1280};
    boss.sprite=128;boss.hitbox_radius={384,768};boss.additional[0]=0;
    return {boss,midboss};
}
}

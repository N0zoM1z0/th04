#include "stage_session.hpp"

namespace th04::portable::session {
void initialize_actors(Actors o,const std::function<std::uint8_t()>& next_byte) {
    o.player.reset_stage_position();
    auto shots=o.shots.snapshot();shots.entities={};
    // shots_reset clears time/style, but NOT Reimu's volley cycle, hit-spark
    // cycle, option coordinates, laser geometry or the collision-cache owner.
    shots.time=0;shots.laser.time=0;shots.laser.style=shot::LaserStyle::two;
    o.shots=shot::System(shots);
    auto enemies=o.enemies.snapshot();enemies.entities={};enemies.player_hit=false;
    o.enemies=enemy::System(enemies);
    auto bullets=o.bullets.snapshot();bullets.entities={};
    bullets.zap_frame=0;bullets.graze=0;bullets.slowdown=1;bullets.player_hit=false;
    // Template, clear timer, counters and score mirrors are outside the clear
    // extent. Preserve them; the first ordinary update owns visibility/cache.
    o.bullets=bullet::System(bullets);
    auto sparks=o.sparks.snapshot();sparks.entities={};o.sparks=spark::System(sparks);
    auto gathers=o.gathers.snapshot();gathers.entities={};
    gathers.scratch.velocity={};gathers.scratch.radius=1024;
    gathers.scratch.ring_points=8;gathers.scratch.color=9;gathers.scratch.angle_delta=2;
    o.gathers=gather::System(gathers);
    auto circles=o.circles.snapshot();circles.entities={};circles.color=13;
    o.circles=circle::System(circles);o.items.reset_stage();
    o.awards.stage_point_items_collected=0;o.awards.dream_items_collected=0;
    o.awards.dream_score=0;
    o.random.fill(next_byte);
    o.drops=item::EnemyDropSequence(static_cast<std::uint8_t>(next_byte()&15));
    o.sparks.initialize(next_byte); // Clears ONLY the low ring-offset byte.
    score::render(o.scoreboard); // HUD update does not drain pending score.
}
midboss::Snapshot prepare_stage2_midboss(midboss::Snapshot s) {
    s.active=false;s.start_frame=2600;s.hp=750;s.sprite=0;
    s.position.current=s.position.previous={3072,-512};s.position.velocity={0,16};
    return s;
}
midboss::Snapshot prepare_stage3_midboss(midboss::Snapshot s) {
    s.active=false;s.start_frame=1600;s.hp=850;s.sprite=0;
    s.position.current=s.position.previous={3072,-512};s.position.velocity={0,64};
    return s;
}
midboss::Snapshot prepare_stage4_midboss(midboss::Snapshot s) {
    s.active=false;s.start_frame=2800;s.hp=1200;s.sprite=0;
    s.position.current=s.position.previous={2304,-512};s.position.velocity={64,32};return s;
}
} // namespace th04::portable::session

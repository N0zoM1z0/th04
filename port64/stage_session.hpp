#pragma once
#include "player_motion.hpp"
#include "player_shots.hpp"
#include "enemy_system.hpp"
#include "enemy_bullets.hpp"
#include "effects.hpp"
#include "circles.hpp"
#include "item_pool.hpp"
#include "score.hpp"
#include "midboss.hpp"

namespace th04::portable::session {
// References to the existing MAIN owners, not a second simulation or a
// serialized DOS layout. Stage reset must retain their process-wide metadata.
struct Actors {
    player::Movement& player;
    shot::System& shots;
    enemy::System& enemies;
    bullet::System& bullets;
    spark::System& sparks;
    gather::System& gathers;
    circle::System& circles;
    item::Pool& items;
    item::ScoreState& awards;
    score::Snapshot& scoreboard;
    randring::SharedRandomRing& random;
    item::EnemyDropSequence& drops;
};
// stage_state_init + the implemented actor callees of stage_runtime_init.
// Other HUD/Bomb/laser/popup/hardware callees are outside this actor boundary.
// Uses353 draws from the SAME process LCG: ring256, drop1, sparks96.
void initialize_actors(Actors,const std::function<std::uint8_t()>& next_byte);
// stage_session_init calls midboss_reset before stage2_setup. Only the latter's
// owned position/start/HP/sprite fields change; inactive animation metadata stays.
midboss::Snapshot prepare_stage2_midboss(midboss::Snapshot previous);
midboss::Snapshot prepare_stage3_midboss(midboss::Snapshot previous);
} // namespace th04::portable::session

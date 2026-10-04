#pragma once
#include "midboss.hpp"
#include "orange.hpp"

namespace th04::portable::stage6 {
struct Setup {
    orange::Snapshot boss;
    midboss::Snapshot midboss;
};
// MAIN13A9:A9EC..AA87 replaces callbacks and these fields only. The Stage5
// CDG/colorfill and private boss globals remain owned by their preceding load.
Setup prepare(orange::Snapshot previous_boss, midboss::Snapshot previous_midboss,
              unsigned rank);
} // namespace th04::portable::stage6

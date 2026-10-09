#pragma once
#include "midboss.hpp"
#include "orange.hpp"

namespace th04::portable::stagex {
struct Setup { orange::Snapshot boss; midboss::Snapshot midboss; };
// MAIN13A9:AA88..AB48. Stage reset precedes this setup; retain fields that
// neither reset nor setup owns. Extra does not use ordinary rank selectors.
Setup prepare(orange::Snapshot previous_boss,midboss::Snapshot previous_midboss);
}

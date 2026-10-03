#include "src/shared/runtime/api.hpp"

// Process-local 32-bit LCG state. Each newly loaded executable begins at 1
// unless its product code copies a seed from the resident block first. The
// resident `rand` field is therefore a seed source, not this live LCG state.
//
// Although the ABI exposes signed long storage, the update casts it to
// unsigned long before multiplication. TC4J consequently keeps the low 32
// bits of (state * 0x015A4E35 + 1), including across the signed boundary. The
// multiplier matches the historical PC-98 master-library LCG family; this
// product owner makes no target-byte claim.
long __cdecl random_seed = 1;

int TH04_PASCAL irand(void)
{
	const unsigned long next_state =
		((unsigned long)random_seed * 0x015A4E35UL) + 1UL;
	random_seed = (long)next_state;

	// Return bits 16..30. The mask keeps the 16-bit result nonnegative and
	// deliberately discards both the low 16 state bits and the top state bit.
	return (int)((next_state >> 16) & 0x7FFFUL);
}

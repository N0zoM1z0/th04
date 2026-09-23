// OP's two-column high-score loader.
#include "src/op/score/scoredat.hpp"
#include "src/shared/runtime/api.hpp"

extern unsigned char rank;
unsigned char pascal near scoredat_decode(void);
void near scoredat_recreate(void);

#pragma codeseg SCORE_TEXT op_01
bool near hiscore_scoredat_load_both(void)
#include "src/op/score/load_both.inl"
#pragma codeseg

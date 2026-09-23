// OP SCORE_TEXT score-file regeneration, reconstructed from target bytes.
#include "src/op/score/scoredat.hpp"
#include "src/shared/runtime/api.hpp"

unsigned char pascal near scoredat_decode(void);
void pascal near scoredat_encode(void);

#pragma codeseg SCORE_TEXT op_01
void near scoredat_recreate(void)
#include "src/op/score/scoregen.inl"
#pragma codeseg

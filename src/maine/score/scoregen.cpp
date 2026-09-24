// MAINE SCORE_TEXT score-file initialization reconstructed from target flow.
#include "src/maine/score/scoredat.hpp"
#include "src/shared/runtime/api.hpp"

unsigned char pascal near scoredat_decode(void);
void pascal near scoredat_encode(void);
extern const char SCOREDAT_FN[];

#pragma codeseg SCORE_TEXT score_01
void near scoredat_recreate(void)
#include "src/maine/score/scoregen.inl"
#pragma codeseg

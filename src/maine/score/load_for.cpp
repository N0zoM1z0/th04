#include "src/maine/score/scoredat.hpp"
#include "src/maine/score/playchar.hpp"
#include "src/shared/runtime/api.hpp"

extern unsigned char rank;
extern const char SCOREDAT_FN_0[];
extern const char SCOREDAT_FN_1[];
unsigned char pascal near scoredat_decode(void);
void near scoredat_recreate(void);

#pragma codeseg SCORE_TEXT score_01
#include "src/maine/score/load_for.inl"
#pragma codeseg

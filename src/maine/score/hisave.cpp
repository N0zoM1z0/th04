#include "src/maine/score/scoredat.hpp"
#include "src/shared/runtime/api.hpp"

extern unsigned char rank;
extern unsigned char playchar;


unsigned char pascal near scoredat_decode(void);
unsigned char pascal near scoredat_encode(void);

#pragma codeseg SCORE_TEXT hiscore_save_01
#include "src/maine/score/hisave.inl"
#pragma codeseg

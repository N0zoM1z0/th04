#include "src/maine/score/scoredat.hpp"
#include "src/shared/platform/types.hpp"
#include "src/shared/config/resident.hpp"

extern unsigned char entered_place;

// Readable source aliases; the historical symbols remain the external OMF
// contract used by the grouped SCORE_TEXT replay.
#define registration_place entered_place
#define loaded_score_section hi

#if defined(TH04P)
#pragma codeseg SCORE_TEXT GROUP_01
#else
#pragma codeseg SCORE_TEXT score_01
#endif
#include "src/maine/score/score_insert.inl"
#pragma codeseg

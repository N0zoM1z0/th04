#pragma option -zCM4_RENDER_TEXT -zPmain_01

#define TH04_DIALOG_FUSED 1
#include "th04/f_dialog.cpp"

// Create the historical empty DIALOG_TEXT contribution. Transitive dialog
// headers restore the TU default segment, so the shared dialog producer is
// emitted after f_dialog in M4_RENDER_TEXT while retaining the main_01 frame.
#pragma codeseg DIALOG_TEXT "CODE" main_01
#include "th04/dialog.cpp"
#undef TH04_DIALOG_FUSED

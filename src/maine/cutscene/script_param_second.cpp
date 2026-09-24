extern unsigned char near *script_p;
extern int script_param_number_default;

void pascal near script_param_read_number_first(int& ret);

#pragma codeseg CUTSCENE_TEXT cutscene_01
#include "src/maine/cutscene/script_param_second.inl"
#pragma codeseg

#include "src/shared/hardware/graphics.hpp"
#include "src/shared/formats/pi.hpp"

void near raise_bg_allocate_and_snap(void);
void pascal near playchar_title_box_put(int playchar);
void near pic_put(void);

#pragma codeseg OP_01_TEXT playchar_menu_initial_01
#include "src/op/menu/playchar_menu_initial.inl"
#pragma codeseg

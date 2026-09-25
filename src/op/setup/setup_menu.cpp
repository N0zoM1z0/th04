#include "src/shared/hardware/graphics.hpp"
#include "src/shared/hardware/frame_delay.hpp"
#include "src/shared/formats/pi.hpp"

void near setup_bgm_menu(void);
void near setup_se_menu(void);

#pragma codeseg OP_SETUP_TEXT setup_menu_01
#include "src/op/setup/setup_menu.inl"
#pragma codeseg

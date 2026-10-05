#pragma option -zCMAIN_032_TEXT -zPmain_03 -k-

#include <dos.h>
#include "src/main/math/randring.hpp"

extern uint16_t randring_p;

uint16_t pascal near randring2_next16_and(uint16_t mask)
{
    // Reduce only after consuming the next overlapping word from shared state.
    _BX = randring_p;
    _AX = reinterpret_cast<uint16_t near &>(randring[_BX]);
    reinterpret_cast<uint8_t near &>(randring_p)++;

    // With mask = width - 1, this is the range shortcut for power-of-two width.
    _BX = _SP;
    _AX &= peek(_SS, (_BX + 2)); /* = */ (mask);
    return _AX;
}

#pragma option -k.

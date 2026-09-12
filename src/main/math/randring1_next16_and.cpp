#pragma option -zCCIRCLE_TEXT -zPmain_01 -k-

#include <dos.h>
#include "th04/math/randring.hpp"

extern uint16_t randring_p;

uint16_t pascal near randring1_next16_and(uint16_t mask)
{
    _BX = randring_p;
    _AX = reinterpret_cast<uint16_t near &>(randring[_BX]);
    reinterpret_cast<uint8_t near &>(randring_p)++;
    _BX = _SP;
    _AX &= peek(_SS, (_BX + 2)); /* = */ (mask);
    return _AX;
}

#pragma option -k.

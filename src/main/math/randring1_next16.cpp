#pragma option -zCCIRCLE_TEXT -zPmain_01 -k-

#include "th04/math/randring.hpp"

extern uint16_t randring_p;

uint16_t near randring1_next16(void)
{
    _BX = randring_p;
    _AX = reinterpret_cast<uint16_t near &>(randring[_BX]);
    reinterpret_cast<uint8_t near &>(randring_p)++;
    return _AX;
}

#pragma option -k.

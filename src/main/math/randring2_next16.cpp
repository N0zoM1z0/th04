#pragma option -zCMAIN_032_TEXT -zPmain_03 -k-

#include "th04/math/randring.hpp"

// TH04/TH05 keep the ring cursor in a word but advance only its low byte.
extern uint16_t randring_p;

uint16_t near randring2_next16(void)
{
    _BX = randring_p;
    _AX = reinterpret_cast<uint16_t near &>(randring[_BX]);
    reinterpret_cast<uint8_t near &>(randring_p)++;
    return _AX;
}

#pragma option -k.

#pragma option -zCCIRCLE_TEXT -zPmain_01 -k-

#include "src/main/math/randring.hpp"

extern uint16_t randring_p;

uint16_t near randring1_next16(void)
{
    // Snapshot the shared cursor before reading. The unaligned word load makes
    // adjacent calls overlap by one byte and crosses into randring_p at 255.
    _BX = randring_p;
    _AX = reinterpret_cast<uint16_t near &>(randring[_BX]);

    // Increment after the sample so the boundary word sees cursor low = 0xFF.
    reinterpret_cast<uint8_t near &>(randring_p)++;
    return _AX;
}

#pragma option -k.

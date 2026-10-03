#pragma option -zCCIRCLE_TEXT -zPmain_01 -k-

#include <dos.h>
#include "src/main/math/randring.hpp"

extern uint16_t randring_p;

uint16_t pascal near randring1_next16_and(uint16_t mask)
{
    // Sampling advances the one shared cursor even if the mask later discards
    // most or all of the word.
    _BX = randring_p;
    _AX = reinterpret_cast<uint16_t near &>(randring[_BX]);
    reinterpret_cast<uint8_t near &>(randring_p)++;

    // Preserve the Pascal stack access emitted by the original macro family.
    _BX = _SP;
    _AX &= peek(_SS, (_BX + 2)); /* = */ (mask);
    return _AX;
}

#pragma option -k.

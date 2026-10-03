#pragma option -zCMAIN_032_TEXT -zPmain_03 -k-

#include "src/main/math/randring.hpp"

// This second code-segment-local accessor operates on the same ring and cursor
// as randring1_next16(); it is not an independent enemy/bullet random stream.
extern uint16_t randring_p;

uint16_t near randring2_next16(void)
{
    // Read first, including the cursor-low boundary byte at index 255.
    _BX = randring_p;
    _AX = reinterpret_cast<uint16_t near &>(randring[_BX]);

    // Wrapping the low byte leaves the cursor high byte unchanged at zero.
    reinterpret_cast<uint8_t near &>(randring_p)++;
    return _AX;
}

#pragma option -k.

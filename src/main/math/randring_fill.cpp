#pragma option -zCCIRCLE_TEXT -zPmain_01 -k-

// The target keeps the ring cursor as a word and fills the shared 256-byte
// ring backward. These declarations are bounded to this MAIN producer.
extern unsigned char randring[256];
extern unsigned short randring_p;
extern "C" unsigned char pascal far IRand(void);

void near randring_fill(void)
{
    register int ring_index;
    ring_index = 255;
    do {
        randring[ring_index] = IRand();
    } while (--ring_index >= 0);

    // Clear both cursor bytes. Accessors subsequently advance only the low
    // byte, so the high byte remains zero for the entire stage session.
    randring_p = 0;
}

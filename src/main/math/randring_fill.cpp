#pragma option -zCCIRCLE_TEXT -zPmain_01 -k-

// The target keeps the ring cursor as a word and fills the 256-byte ring
// backward. These declarations are bounded to this MAIN producer.
extern unsigned char randring[256];
extern unsigned short randring_p;
extern "C" unsigned char pascal far IRand(void);

void near randring_fill(void)
{
    register int i;
    i = 255;
    do {
        randring[i] = IRand();
    } while (--i >= 0);
    randring_p = 0;
}

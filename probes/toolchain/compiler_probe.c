/* Independent Turbo C++/TLINK smoke probe; not target-derived code. */
#include <dos.h>

unsigned long probe_mix(unsigned int left, unsigned int right)
{
	return (((unsigned long)left << 16) | right) ^ 0x13579BDFUL;
}

int main(void)
{
	return (probe_mix(0x1234U, 0x5678U) == 0x0163CDA7UL) ? 0 : 1;
}

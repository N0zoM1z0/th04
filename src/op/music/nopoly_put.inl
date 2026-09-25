void near nopoly_B_put(void)
{
	memcpy(
		(void far *)(unsigned char __seg *)0xA800,
		(const void far *)nopoly_B,
		0x7D00
	);
}

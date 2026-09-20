void near item_splashes_init(void)
{
	// memset(item_splashes, 0x00, sizeof(item_splashes));
	_CX = (sizeof(item_splashes) / sizeof(uint16_t));
	_ES = _DS;
	asm { xor ax, ax; }
	reinterpret_cast<item_splash_t near *>(_DI) = item_splashes;
	asm { rep stosw; }

	item_splash_last_id = 0;
}


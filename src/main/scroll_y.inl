vram_y_t pascal near scroll_subpixel_y_to_vram_seg3(subpixel_t y)
{
	#define ret static_cast<vram_y_t>(_AX) // Must be signed!

	_BX = _SP;
	ret = peek(_SS, (_BX + 2)); /* = */ (y);

	ret = TO_PIXEL(ret);
	if(scroll_active) {
		ret += scroll_line;
	}
	ret = roll(ret);
	return ret;

	#undef ret
}

vram_y_t pascal near scroll_subpixel_y_to_vram_always(subpixel_t y)
{
	#define ret static_cast<vram_y_t>(_AX) // Must be signed!

	_BX = _SP;
	ret = peek(_SS, (_BX + 2)); /* = */ (y);

	ret = (TO_PIXEL(ret) + scroll_line);
	ret = roll(ret);
	return ret;

	#undef ret
}

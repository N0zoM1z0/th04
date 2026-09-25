void near pic_put(void)
{
	if(playchar_menu_sel == PLAYCHAR_REIMU) {
		pic_put_for(PLAYCHAR_REIMU, REIMU_LEFT, MARISA_LEFT);
	} else {
		pic_put_for(PLAYCHAR_MARISA, MARISA_LEFT, REIMU_LEFT);
	}
}

void near shottype_menu_put_initial(void)
{
	if(playchar_menu_sel == PLAYCHAR_REIMU) {
		cdg_put_noalpha_8(
			SHOTTYPE_PIC_LEFT, SHOTTYPE_PIC_TOP, (CDG_PIC + PLAYCHAR_REIMU)
		);
	} else {
		cdg_put_noalpha_8(
			SHOTTYPE_PIC_LEFT, SHOTTYPE_PIC_TOP, (CDG_PIC + PLAYCHAR_MARISA)
		);
	}

	grcg_setcolor(GC_RMW, COL_SHADOW);
	grcg_boxfill_8(
		(SHOTTYPE_PIC_LEFT + PIC_W),
		(SHOTTYPE_PIC_TOP + RAISE_W),
		(SHOTTYPE_PIC_LEFT + PIC_W),
		(SHOTTYPE_PIC_TOP + PIC_H - 1)
	);
	grcg_boxfill_8(
		(SHOTTYPE_PIC_LEFT + RAISE_W),
		(SHOTTYPE_PIC_TOP + PIC_H),
		(SHOTTYPE_PIC_LEFT + PIC_W),
		(SHOTTYPE_PIC_TOP + PIC_H + RAISE_H - 1)
	);
	outportb(0x7C, 0);
	shottype_title_box_put();
	shottype_titles_put(shottype_menu_sel);
}

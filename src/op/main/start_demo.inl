void near start_demo(void)
{
	// ZUN bloat: This is reassigned to [resident->demo_stage] shortly after
	// the start of MAIN.EXE. Would be cleaner to do it here, which would even
	// avoid the need for a distinct demo stage field altogether.
	resident->stage = 0;

	resident->credit_lives = 3;
	resident->credit_bombs = 3;

	resident->demo_num++;
	if(resident->demo_num > 4) {
		resident->demo_num = 1;
	}

	switch(resident->demo_num) {
	case 1:
		resident_set_demo(3, PLAYCHAR_REIMU, SHOTTYPE_A);
		break;
	case 2:
		resident_set_demo(0, PLAYCHAR_MARISA, SHOTTYPE_A);
		break;
	case 3:
		resident_set_demo(2, PLAYCHAR_REIMU, SHOTTYPE_B);
		break;
	case 4:
		resident_set_demo(1, PLAYCHAR_MARISA, SHOTTYPE_B);
		break;
	}
	palette_black_out(1);
	super_free();
	pi_free(0); // ZUN bloat: OP.EXE doesn't leave any .PI image in memory.
	op_exit_into_main(false, false);
}

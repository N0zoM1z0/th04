void near end_animate(void)
{
	static char* SCRIPT_FN = "_ED000.TXT";
	SCRIPT_FN[3] = resident->playchar_ascii;
	SCRIPT_FN[4] = ('0' + resident->shottype);
	SCRIPT_FN[5] = resident->end_type_ascii;
	cutscene_script_load(SCRIPT_FN);
	cutscene_animate();
	cutscene_script_free();
}

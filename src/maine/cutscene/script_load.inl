int pascal near cutscene_script_load(const char far *fn)
{
	cutscene_script_free();

	if(!file_ropen(fn)) {
		return 1;
	}
	unsigned int size = file_size();
	script_p = script;
	file_read(script_p, size);
	file_close();
	return 0;
}

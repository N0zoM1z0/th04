void pascal near script_param_read_number_second(int& ret)
{
	if(*script_p == ',') {
		script_p++;
		script_param_read_number_first(ret);
	} else {
		ret = script_param_number_default;
	}
}

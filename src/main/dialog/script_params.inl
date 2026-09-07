void pascal near script_param_read_number_first(int& ret)
{
	unsigned char c0 = *script_p; script_p++;
	unsigned char c1 = *script_p; script_p++;
	unsigned char c2 = *script_p; script_p++;
	if(!isdigit(c0)) {
		ret = script_param_number_default;
		script_p -= 3;
	} else if(!isdigit(c1)) {
		ret = (c0 - '0');
		script_p -= 2;
	} else if(!isdigit(c2)) {
		ret = (((c0 - '0') * 10) + c1 - '0');
		script_p -= 1;
	} else {
		ret = (((c0 - '0') * 100) + ((c1 - '0') * 10) + (c2 - '0'));
	}
}

inline void script_param_read_number_first(int& ret, int default_value) {
	script_param_number_default = default_value;
	script_param_read_number_first(ret);
}

void pascal near script_param_read_number_second(int& ret)
{
	if(*script_p == ',') {
		script_p++;
		script_param_read_number_first(ret);
	} else {
		ret = script_param_number_default;
	}
}

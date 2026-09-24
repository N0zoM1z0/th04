static const unsigned char DIGIT_MASK = 2;

void pascal near script_param_read_number_first(int& ret)
{
	unsigned char c0 = *script_p;
	script_p++;
	unsigned char c1 = *script_p;
	script_p++;
	unsigned char c2 = *script_p;
	script_p++;

	if(!(_ctype[c0 + 1] & DIGIT_MASK)) {
		ret = script_param_number_default;
		script_p -= 3;
	} else if(!(_ctype[c1 + 1] & DIGIT_MASK)) {
		ret = (c0 - '0');
		script_p -= 2;
	} else if(!(_ctype[c2 + 1] & DIGIT_MASK)) {
		ret = (((c0 - '0') * 10) + c1 - '0');
		script_p--;
	} else {
		ret = (
			((c0 - '0') * 100) +
			((c1 - '0') * 10) +
			(c2 - '0')
		);
	}
}

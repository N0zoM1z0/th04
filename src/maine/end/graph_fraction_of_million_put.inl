void pascal near graph_fraction_of_million_put(
	screen_x_t left, screen_y_t top, uint32_t num
)
{
	register screen_x_t left_reg = left;
	register screen_y_t top_reg = top;
	uint16_t digits;
	digits = (num / 10000UL);
	graph_3_digit_put(left_reg, top_reg, digits);
	num %= 10000UL;
	digits = (num / 100UL);
	graph_3_digit_put_as_fixed_2_digit = true;
	graph_3_digit_put((left_reg + 48), top_reg, digits);
	graph_3_digit_put_as_fixed_2_digit = false;
	graph_putsa_fx((left_reg + 48), top_reg, 14, aBd_0);
}

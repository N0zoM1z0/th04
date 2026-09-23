// Bounded semantic body; alphabet_cursor_put is a descriptive name.
void pascal near alphabet_cursor_put(int col, int row, int color)
{
    register int col_r = col;
    register int row_r = row;
    gaiji_putca(
        ((col_r * 2) + 23), (row_r + 18),
        gALPHABET[(row_r * 17) + col_r], color
    );
}

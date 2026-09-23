// Bounded semantic body; the name is descriptive, not original-source proof.
void pascal near name_cursor_put(int place, unsigned char rendered_playchar, unsigned char cursor)
{
    int y;
    register int place_r = place;
    register int x;

    x = ((rendered_playchar == 0) ? 2 : 40);
    y = ((place_r == 0) ? 6 : (place_r + 7));

    score_rect_copy(((x * 8) + 2), ((y * 16) + 2), 128, 16);
    graph_gaiji_puts(
        ((x * 8) + 2), ((y * 16) + 2), GAIJI_W,
        reinterpret_cast<const char*>(hi.score.g_name[place_r]), 14
    );
    gaiji_putsa(x, y, reinterpret_cast<const char*>(hi.score.g_name[place_r]), TX_RED);
    gaiji_putca(
        (x + (cursor * 2)), y,
        hi.score.g_name[place_r][cursor],
        (TX_RED + TX_REVERSE)
    );
}

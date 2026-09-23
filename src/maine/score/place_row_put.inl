// Bounded semantic body; place_row_put is a descriptive name.
void pascal near place_row_put(int place, unsigned char rendered_playchar)
{
    int x;
    register int place_r = place;
    register int y;

    x = ((rendered_playchar == 0) ? 16 : 320);
    y = ((place_r == 0) ? 96 : ((place_r * 16) + 112));

    graph_gaiji_puts(
        (x + 2), (y + 2), GAIJI_W,
        reinterpret_cast<const char *>(hi.score.g_name[place_r]), 14
    );
    if (
        (entered_place != place_r) ||
        (rendered_playchar != static_cast<unsigned char>(playchar))
    ) {
        graph_gaiji_puts(
            x, y, GAIJI_W,
            reinterpret_cast<const char *>(hi.score.g_name[place_r]), 12
        );
    } else {
        gaiji_putsa(
            (x / 8), (y / 16),
            reinterpret_cast<const char *>(hi.score.g_name[place_r]), TX_RED
        );
    }
    score_put(place_r, rendered_playchar);
    stage_put(place_r, rendered_playchar, hi.score.g_stage[place_r]);
}

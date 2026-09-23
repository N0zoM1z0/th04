// Bounded semantic body; stage_put is descriptive, not original-name evidence.
void pascal near stage_put(int place, int rendered_playchar, int gaiji)
{
    int x;
    int y;
    unsigned char col;
    register int place_r = place;
    register int playchar_r = rendered_playchar;

    col = (((entered_place == place_r) &&
            (playchar_r == static_cast<unsigned char>(playchar))) ? 7 : 12);
    y = ((place_r == 0) ? 96 : ((place_r * 16) + 112));
    x = ((playchar_r == PLAYCHAR_REIMU) ? 292 : 600);

    graph_gaiji_putc((x + 2), (y + 2), gaiji, 14);
    graph_gaiji_putc(x, y, gaiji, col);
}

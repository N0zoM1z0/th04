// Bounded semantic body; stage_put is descriptive, not an original-name claim.
void pascal near stage_put(int left, int top, int gaiji)
{
    if(gaiji != g_NONE) {
        graph_gaiji_putc((left + 2), (top + 2), gaiji, COL_SHADOW);
        graph_gaiji_putc(left, top, gaiji, COL_STAGE);
    } else {
        graph_gaiji_putc((left + 2), (top + 2), g_HISCORE_STAGE_EMPTY, COL_SHADOW);
        graph_gaiji_putc(left, top, g_HISCORE_STAGE_EMPTY, COL_STAGE);
    }
}

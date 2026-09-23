// Bounded natural body; place_put is descriptive, not original-source proof.
void pascal near place_put(int place)
{
    if (place == 0) {
        names_put(TABLE_TOP, COL_NAME_FIRST, place);
        scores_put(TABLE_TOP, 0);
        stages_put(TABLE_TOP, place);
    } else {
        screen_y_t top = (
            TABLE_TOP + PLACE_1_PADDING_BOTTOM + (place * GLYPH_H)
        );
        names_put(top, COL_NAME, place);
        scores_put(top, place);
        stages_put(top, place);
    }
}

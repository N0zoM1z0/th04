// Bounded body included by score_put.cpp and the grouped SCORE_TEXT replay.
// The descriptive name is not attested as an original source symbol.
void pascal near score_put(int place, unsigned char rendered_playchar)
{
    int digit;
    int y;
    register int place_r = place;
    register int x;

    y = ((place_r == 0) ? 96 : ((place_r * 16) + 112));
    x = ((rendered_playchar == PLAYCHAR_REIMU) ? 172 : 480);

    rendered_playchar = (
        ((entered_place == place_r) && (rendered_playchar == static_cast<unsigned char>(playchar))) ? 10 : 0
    );

    if((hi.score.g_score[place_r].digits[SCORE_DIGITS - 1] - gb_0) >= 10) {
        super_put(
            (x - 32), y,
            (((hi.score.g_score[place_r].digits[SCORE_DIGITS - 1] - gb_0) / 10) + rendered_playchar)
        );
    }
    super_put(
        (x - 16), y,
        (((hi.score.g_score[place_r].digits[SCORE_DIGITS - 1] - gb_0) % 10) + rendered_playchar)
    );
    for(digit = 6; digit >= 0; digit--, x += 16) {
        super_put(
            x, y,
            (hi.score.g_score[place_r].digits[digit] + rendered_playchar - gb_0)
        );
    }
}

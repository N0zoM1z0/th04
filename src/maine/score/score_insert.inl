// Bounded body included by insert.cpp and the grouped SCORE_TEXT replay.
// score_insert is a descriptive name; the target does not attest its spelling.
void near score_insert(void)
{
    int compared_place;
    int digit_index;

    // Walk upward from the lowest table row. Each stored score byte is a gaiji
    // digit (gb_0 + 0..9), while resident->score_last holds numeric digits.
    // Equal scores keep walking upward, so the new result precedes existing
    // equal results. Preserve the descending digit order used by the target.
    for(
        compared_place = (SCOREDAT_PLACES - 1);
        compared_place >= 0;
        compared_place--
    ) {
        for(digit_index = (SCORE_DIGITS - 1); digit_index >= 0; digit_index--) {
            if(
                resident->score_last.digits[digit_index] >
                (loaded_score_section.score.g_score[compared_place]
                    .digits[digit_index] - gb_0)
            ) {
                break;
            }
            if(
                resident->score_last.digits[digit_index] <
                (loaded_score_section.score.g_score[compared_place]
                    .digits[digit_index] - gb_0)
            ) {
                goto lower_than_compared_place;
            }
        }
    }
    registration_place = 0;
    goto shift_lower_places;

lower_than_compared_place:
    if(compared_place == (SCOREDAT_PLACES - 1)) {
        // Lower than the last row: leave the table untouched and publish the
        // unsigned 0xFF sentinel consumed by regist_menu().
        registration_place = -1;
        return;
    }
    registration_place = (compared_place + 1);

shift_lower_places:
    // Open the selected row by copying lower rows downward. The ninth name
    // byte is a persistent NUL terminator initialized by scoredat_recreate(),
    // so only the eight editable glyphs move here.
    for(
        compared_place = (SCOREDAT_PLACES - 2);
        compared_place >= registration_place;
        compared_place--
    ) {
        for(
            digit_index = (SCOREDAT_NAME_LEN - 1);
            digit_index >= 0;
            digit_index--
        ) {
            loaded_score_section.score.g_name[compared_place + 1][digit_index] =
                loaded_score_section.score.g_name[compared_place][digit_index];
        }
        for(digit_index = (SCORE_DIGITS - 1); digit_index >= 0; digit_index--) {
            loaded_score_section.score.g_score[compared_place + 1]
                .digits[digit_index] = loaded_score_section.score
                .g_score[compared_place].digits[digit_index];
        }
        loaded_score_section.score.g_stage[compared_place + 1] =
            loaded_score_section.score.g_stage[compared_place];
    }

    // Initialize the new editable name, convert the numeric resident score to
    // display gaiji, and store either the reached stage or the ALL marker used
    // for Extra/Ending states (their end_sequence values are >= ES_EXTRA).
    for(digit_index = (SCOREDAT_NAME_LEN - 1); digit_index >= 0; digit_index--) {
        loaded_score_section.score.g_name[registration_place][digit_index] =
            gs_DOT;
    }
    for(digit_index = (SCORE_DIGITS - 1); digit_index >= 0; digit_index--) {
        loaded_score_section.score.g_score[registration_place]
            .digits[digit_index] = (
                resident->score_last.digits[digit_index] + gb_0
            );
    }
    if(resident->end_sequence >= ES_EXTRA) {
        loaded_score_section.score.g_stage[registration_place] = gs_ALL;
    } else {
        loaded_score_section.score.g_stage[registration_place] = (
            resident->stage + gb_1
        );
    }
}

// Target-restored MAINE SCORE_TEXT owner at 1A05:225D (payload 0xC2AD).
extern const char SCOREDAT_FN_0[];
extern const char SCOREDAT_FN_1[];

bool pascal near hiscore_scoredat_load_for(playchar_t requested_playchar)
{
    // GENSOU.SCR contains two character blocks of five rank sections. Load
    // exactly one 196-byte section into the shared decoded/encoded work buffer.
    // Preserve the target's separate filename symbols and unchecked open/read
    // calls: they are part of the accepted grouped SCORE_TEXT shape.
    if(file_exist(SCOREDAT_FN_0)) {
        file_ropen(SCOREDAT_FN_1);
        file_seek(
            (registration_rank * sizeof(scoredat_section_t)), SEEK_SET
        );
        if(requested_playchar != PLAYCHAR_REIMU) {
            file_seek(
                (SCOREDAT_RANKS_PER_PLAYCHAR * sizeof(scoredat_section_t)),
                SEEK_CUR
            );
        }
        file_read(&loaded_score_section, sizeof(scoredat_section_t));
        file_close();

        // Decode mutates the buffer in place and returns a nonzero checksum
        // delta on corruption. Replace that one in-memory section with default
        // rows and report the recreation to the caller; saving happens later.
        if(scoredat_decode() != 0) {
            scoredat_recreate();
            return true;
        }
    } else {
        // A missing file follows the same in-memory recreation path. This
        // helper does not create or write GENSOU.SCR itself.
        scoredat_recreate();
        return true;
    }
    return false;
}

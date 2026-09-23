// Target-restored MAINE SCORE_TEXT owner at 1A05:225D (payload 0xC2AD).
extern const char SCOREDAT_FN_0[];
extern const char SCOREDAT_FN_1[];

bool pascal near hiscore_scoredat_load_for(playchar_t playchar)
{
    if(file_exist(SCOREDAT_FN_0)) {
        file_ropen(SCOREDAT_FN_1);
        file_seek((rank * sizeof(scoredat_section_t)), SEEK_SET);
        if(playchar != PLAYCHAR_REIMU) {
            file_seek((5 * sizeof(scoredat_section_t)), SEEK_CUR);
        }
        file_read(&hi, sizeof(scoredat_section_t));
        file_close();
        if(scoredat_decode() != 0) {
            scoredat_recreate();
            return true;
        }
    } else {
        scoredat_recreate();
        return true;
    }
    return false;
}

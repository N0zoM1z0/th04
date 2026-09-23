void near cleardata_and_regist_view_sprites_load(void)
{
    rank = RANK_EASY;
    while(rank < RANK_COUNT) {
        if(hiscore_scoredat_load_both()) {
            break;
        }
        cleared_with[PLAYCHAR_REIMU][rank] = hi.score.cleared;
        cleared_with[PLAYCHAR_MARISA][rank] = hi2.score.cleared;
        if(cleared_with[PLAYCHAR_REIMU][rank] > SCOREDAT_CLEARED_BOTH) {
            cleared_with[PLAYCHAR_REIMU][rank] = false;
        }
        if(cleared_with[PLAYCHAR_MARISA][rank] > SCOREDAT_CLEARED_BOTH) {
            cleared_with[PLAYCHAR_MARISA][rank] = false;
        }
        if(rank != RANK_EASY) {
            extra_unlocked |= (
                cleared_with[PLAYCHAR_REIMU][rank] |
                cleared_with[PLAYCHAR_MARISA][rank]
            );
        }
        rank++;
    }

    rank = resident->rank;
    super_entry_bfnt("scnum.bft");
    super_entry_bfnt("hi_m.bft");
}

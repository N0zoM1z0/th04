void near regist_view_menu(void)
{
    snd_kaja_func(KAJA_SONG_STOP, 0);
    snd_load(BGM_HISCORE_FN, SND_LOAD_SONG);
    snd_kaja_func(KAJA_SONG_PLAY, 0);
    snd_kaja_func(KAJA_SONG_FADE, -128);

    palette_black_out(1);
    rank = resident->rank;
    hiscore_scoredat_load_both();
    pi_load(0, HISCORE_BG_FN);
    rank_render();
    palette_black_in(1);

    while(1) {
        input_reset_sense();
        frame_delay(1);
        // The repeated OK test is present in the target's branch sequence.
        if((key_det & INPUT_OK) || (key_det & INPUT_SHOT) ||
           (key_det & INPUT_CANCEL) || (key_det & INPUT_OK)) {
            break;
        }
        if((key_det & INPUT_LEFT) && (rank != RANK_EASY)) {
            rank--;
            palette_settone(0);
            hiscore_scoredat_load_both();
            rank_render();
            palette_black_in(1);
        }
        if((key_det & INPUT_RIGHT) && (rank < RANK_EXTRA)) {
            rank++;
            palette_settone(0);
            hiscore_scoredat_load_both();
            rank_render();
            palette_black_in(1);
        }
    }

    snd_kaja_func(KAJA_SONG_FADE, 1);
    palette_black_out(1);
    pi_free(0);
    graph_accesspage(1);
    pi_fullres_load_palette_apply_put_free(0, MENU_MAIN_BG_FN);
    graph_copy_page(0);
    palette_black_in(1);

    do {
        input_reset_sense();
        frame_delay(1);
    } while(key_det != INPUT_NONE);

    snd_kaja_func(KAJA_SONG_STOP, 0);
    snd_load(BGM_MENU_MAIN_FN, SND_LOAD_SONG);
    snd_kaja_func(KAJA_SONG_PLAY, 0);
}

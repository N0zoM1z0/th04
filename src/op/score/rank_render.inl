// Bounded semantic body; rank_render is descriptive, not original-source proof.
void near rank_render(void)
{
    graph_accesspage(1); pi_palette_apply(0); pi_put_8(0, 0, 0);
    graph_accesspage(0); pi_palette_apply(0); pi_put_8(0, 0, 0);

    place_put(0);
    for (int place = 1; place < (SCOREDAT_PLACES - 1); place++) {
        place_put(place);
    }
    place_put(SCOREDAT_PLACES - 1);

    super_put(
        (RANK_LEFT + (0 * (RANK_W / 2))), RANK_TOP, (PAT_RANK_1 + (rank * 2))
    );
    super_put(
        (RANK_LEFT + (1 * (RANK_W / 2))), RANK_TOP, (PAT_RANK_2 + (rank * 2))
    );
}

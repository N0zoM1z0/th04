// Bounded semantic body; places_put is a descriptive name.
void pascal near places_put(int rendered_playchar)
{
    register int place = 0;
    for (; place < SCOREDAT_PLACES; place++) {
        place_row_put(place, rendered_playchar);
    }
}

void pascal near carpet_lighting_put_new(int cel, unsigned int target_level)
{
    for(int tile_x = 0; tile_x < TILES_X; tile_x++) {
        if(CARPET_LIGHTING_ANIM[cel][tile_x] != 1) {
            continue;
        }

        const vram_offset_t image_vo = CARPET_TILE_IMAGE_VOS[target_level][tile_x];
        for(int tile_y = 0; tile_y < TILES_Y; tile_y++) {
            tile_ring[tile_y][tile_x] = image_vo;
        }
        for(int flag_y = 0; flag_y < TILE_FLAGS_Y; flag_y++) {
            halftiles_dirty[flag_y][tile_x] = true;
        }
    }
}

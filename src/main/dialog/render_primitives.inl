void pascal near dialog_box_put(uscreen_x_t left, uvram_y_t top, int tile)
{
    #define rows_left static_cast<pixel_t>(_DX)
    #define offset static_cast<uint16_t>(_BX)

    grcg_setcolor(GC_RMW, 1);
    _ES = SEG_PLANE_B;
    _AX = left;
    _DX = top;
    _DI = vram_offset_shift_fast(_AX, _DX);

    static_assert(BOX_TILE_SIZE == 8);
    offset = tile;
    offset <<= 3;
    rows_left = BOX_H;

    do {
        _CX = (BOX_VRAM_W / sizeof(egc_temp_t));
        _AX = *reinterpret_cast<const dots_t(BOX_TILE_W) __ds *>(
            reinterpret_cast<const uint8_t __ds *>(BOX_TILES) + offset
        );
        do {
            *reinterpret_cast<egc_temp_t __es *>(_DI) = _AX;
            _DI += sizeof(egc_temp_t);
        } while(--_CX);

        offset += BOX_TILE_VRAM_W;
        if((offset & (BOX_TILE_SIZE - 1)) == 0) {
            offset -= BOX_TILE_SIZE;
        }
        _DI += (ROW_SIZE - BOX_VRAM_W);
    } while(--rows_left);

    grcg_off();

    #undef offset
    #undef rows_left
}

#define egc_rect_interpage_16(bottom_p, w, src_page) { \
    _DX = 0xA6; \
    _AL = src_page; \
    do { \
        _CX = (w / EGC_REGISTER_DOTS); \
        do { \
            outportb(_DX, _AL); \
            _AL ^= 1; \
            _BX = *bottom_p; \
            outportb(_DX, _AL); \
            _AL ^= 1; \
            *bottom_p = _BX; \
            bottom_p++; \
        } while(--_CX); \
    } while(((int16_t)(bottom_p) -= ((RES_X + w) / BYTE_DOTS)) >= 0); \
}

void near playfield_copy_front_to_back(void)
{
    egc_start_copy_noframe();
    _ES = grcg_segment(0, PLAYFIELD_TOP);
    _DI = (((PLAYFIELD_H - 1) * ROW_SIZE) + PLAYFIELD_VRAM_LEFT);
    egc_rect_interpage_16(
        reinterpret_cast<egc_temp_t __es *>(_DI), PLAYFIELD_W, page_front
    );
    outportb(_DX, _AL);
    egc_off();
}

void pascal near dialog_face_unput_8(uscreen_x_t left, uvram_y_t top)
{
    egc_start_copy_noframe();

    _AX = top;
    _BX = _AX;
    _ES = (SEG_PLANE_B + ((_AX * 4) + _BX));

    _DI = ((FACE_H - 1) * ROW_SIZE);
    _DI += (left / BYTE_DOTS);
    egc_rect_interpage_16(
        reinterpret_cast<egc_temp_t __es *>(_DI), FACE_W, page_back
    );
    egc_off();
}

#undef egc_rect_interpage_16

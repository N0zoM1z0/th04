// OP SCORE_TEXT two-column high-score row renderer.
#include "src/op/score/scoredat.hpp"
#include "src/shared/hardware/graphics.hpp"

enum {
    PLAYCHAR_REIMU = 0,
    PLAYCHAR_MARISA = 1,
    COL_NAME = 2,
    COL_NAME_FIRST = 7,
    COL_SHADOW = 14,
};

static const pixel_t DIGIT_W = 16;
static const pixel_t NAME_W = (SCOREDAT_NAME_LEN * GAIJI_W);
static const pixel_t NAME_PADDED_W = (NAME_W + 4 + DIGIT_W);
static const pixel_t SCORE_PADDED_W = ((DIGIT_W * SCORE_DIGITS) + 8);
static const pixel_t STAGE_PADDED_W = (GAIJI_W + 8);
static const pixel_t COLUMN_W = (NAME_PADDED_W + SCORE_PADDED_W + STAGE_PADDED_W);
static const screen_x_t NAME_LEFT = 8;
static const screen_x_t SCORE_LEFT = (NAME_LEFT + NAME_PADDED_W);
static const screen_x_t STAGE_LEFT = (SCORE_LEFT + SCORE_PADDED_W);
static const screen_y_t TABLE_TOP = 96;
static const pixel_t PLACE_1_PADDING_BOTTOM = GLYPH_H;

void pascal near scores_put(screen_y_t top, int place);
void pascal near stage_put(screen_x_t left, screen_y_t top, int gaiji);

#define name_put_shadowed(left, top, str, col_fg) { \
    graph_gaiji_puts(((left) + 2), ((top) + 2), GAIJI_W, str, COL_SHADOW); \
    graph_gaiji_puts(((left) + 0), ((top) + 0), GAIJI_W, str, col_fg); \
}

#define names_put(top, col_fg, place) { \
    name_put_shadowed( \
        (NAME_LEFT + (PLAYCHAR_REIMU * (COLUMN_W + 4))), top, \
        reinterpret_cast<const char far *>(hi.score.g_name[place]), col_fg \
    ); \
    name_put_shadowed( \
        (NAME_LEFT + (PLAYCHAR_MARISA * (COLUMN_W + 4))), top, \
        reinterpret_cast<const char far *>(hi2.score.g_name[place]), col_fg \
    ); \
}

#define stages_put(top, place) { \
    stage_put((STAGE_LEFT + (PLAYCHAR_REIMU * COLUMN_W)), top, hi.score.g_stage[place]); \
    stage_put((STAGE_LEFT + (PLAYCHAR_MARISA * COLUMN_W)), top, hi2.score.g_stage[place]); \
}

#pragma codeseg SCORE_TEXT op_01
#include "src/op/score/place_put.inl"
#pragma codeseg

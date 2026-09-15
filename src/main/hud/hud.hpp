#ifndef TH04_MAIN_HUD_HUD_HPP
#define TH04_MAIN_HUD_HUD_HPP

// Keep these aggregate types outside the source-level -a2 switch-table pragma;
// their byte layout is part of the target TC4J code shape.
struct hud_bar9_t {
    unsigned char v[9];
};

struct hud_colors10_t {
    unsigned char v[10];
};

struct hud_colors5_t {
    unsigned char v[5];
};

extern "C" void pascal near score_extend_update_and_render(void);
void near score_reset(void);
void far hud_lives_put(void);
void far hud_bombs_put(void);
extern "C" void pascal far hud_point_items_put(void);
extern "C" void pascal far hud_dream_put(void);
void far hud_graze_put(void);
extern "C" void pascal far hud_power_put(void);
void pascal far hud_hp_put(int bar_value);
extern "C" void pascal far hud_bar_put(int y, int value, int atrb);
void far hud_put(void);

#endif

#ifndef TH04_BGIMAGE_HPP
#define TH04_BGIMAGE_HPP

#include <stddef.h>

// Four 32,000-byte buffers, one segment pointer per PC-98 VRAM plane.
// The target stores these words at consecutive offsets B, R, G, E.
struct bgimage_planes_t {
    unsigned char __seg *B;
    unsigned char __seg *R;
    unsigned char __seg *G;
    unsigned char __seg *E;
};

typedef char bgimage_layout_check[
    (sizeof(bgimage_planes_t) == 8) &&
    (offsetof(bgimage_planes_t, B) == 0) &&
    (offsetof(bgimage_planes_t, R) == 2) &&
    (offsetof(bgimage_planes_t, G) == 4) &&
    (offsetof(bgimage_planes_t, E) == 6) ? 1 : -1
];

extern bgimage_planes_t bgimage;

extern "C" {
void bgimage_snap(void);
void bgimage_put(void);
void bgimage_free(void);
}

#endif

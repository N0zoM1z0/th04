#ifndef TH04_MAIN_PLAYFLD_HPP
#define TH04_MAIN_PLAYFLD_HPP

#include "src/main/math/subpixel.hpp"
#include "src/main/math/motion.hpp"

#define PLAYFIELD_LEFT 32
#define PLAYFIELD_TOP 16
#define PLAYFIELD_W 384
#define PLAYFIELD_H 368
#define PLAYFIELD_RIGHT (PLAYFIELD_LEFT + PLAYFIELD_W)
#define PLAYFIELD_BOTTOM (PLAYFIELD_TOP + PLAYFIELD_H)

// MAIN stores gameplay coordinates relative to the playfield in Q12.4 form.
struct PlayfieldPoint : public SPPoint {
};

struct PlayfieldMotion : public MotionBase<PlayfieldPoint> {
	PlayfieldPoint pascal near update_seg1();
	PlayfieldPoint pascal near update_seg3();
};

#endif

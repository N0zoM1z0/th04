struct resident_t;

struct cfg_options_t {
	signed char rank;
	signed char lives;
	signed char bombs;
	signed char bgm_mode;
	signed char se_mode;
	signed char turbo_mode;
};

struct cfg_t {
	cfg_options_t opts;
	resident_t __seg *resident;
	signed char debug;
	signed char opts_sum;
};

extern resident_t far *resident;

extern "C" {
int far pascal file_ropen(const char far *filename);
int far pascal file_read(void far *buf, unsigned size);
void far pascal file_close(void);
}

#pragma codeseg MAINE_E_TEXT maine_e_01
#include "src/maine/core/cfg_load_resident_ptr.inl"
#pragma codeseg

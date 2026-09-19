// Runtime ABI declarations used by the original TH04 code.

// Keep the vendor guard so an indirect pinned-scaffold include cannot declare
// inline bodies a second time during exact replay.
#ifndef MASTER_HPP
#define MASTER_HPP

#include "src/shared/platform/types.hpp"
#include "src/shared/platform/abi.hpp"
#include "src/shared/platform/x86.hpp"

/// Original functions (only contains those actually called from ZUN code)
/// ----------------------------------------------------------------------

#ifdef __cplusplus
extern "C" {
#endif

// "BGM" (only used for Beep sound effects)
// ----------------------------------------

int TH04_PASCAL bgm_init(int bufsiz);
void TH04_PASCAL bgm_finish(void);
int TH04_PASCAL bgm_read_sdata(const char TH04_PTR *fn);
int TH04_PASCAL bgm_sound(int num);
// ----------------------------------------

// DOS
// ---
// These use INT 21h syscalls as directly as possible.

int TH04_PASCAL dos_getch(void);
void TH04_PASCAL dos_putch(int chr);
void TH04_PASCAL dos_puts(const char TH04_PTR * str);
void TH04_PASCAL dos_puts2(const char TH04_PTR *string);

void TH04_PASCAL dos_free(void __seg *seg);
int TH04_PASCAL dos_create(const char TH04_PTR *filename, int attrib);
int TH04_PASCAL dos_close(int fh);
int TH04_PASCAL dos_write(int fh, const void far *buffer, unsigned len);
long TH04_PASCAL dos_seek(int fh, long offs, int mode);

long TH04_PASCAL dos_axdx(int axval, const char TH04_PTR *strval);
// ---

// EMS
// ---

unsigned TH04_PASCAL ems_allocate(unsigned long len);
int TH04_PASCAL ems_exist(void);
int TH04_PASCAL ems_read(unsigned handle, long offset, void far *mem, long size);
int TH04_PASCAL ems_setname(unsigned handle, const char TH04_PTR * name);
unsigned long TH04_PASCAL ems_space(void);
int TH04_PASCAL ems_write(
	unsigned handle, long offset, const void far *mem, long size
);
// ---

// Joystick
// --------

extern int js_bexist;
extern unsigned js_stat[2];

int TH04_PASCAL js_start();	// ZUN removed the [force] parameter

void TH04_PASCAL js_end(void);
int TH04_PASCAL js_sense(void);
// --------

// super.lib error codes
// ---------------------

#define NoError 0            	/* 正常終了 */
#define FileNotFound -2      	/* ファイル名が見つからない */
#define InsufficientMemory -8	/* メモリ不足 */
#define InvalidData -13      	/* 無効なデータ */
// ---------------------

// Keyboard
// --------

void TH04_PASCAL key_start(void);
void TH04_PASCAL key_end(void);

void TH04_PASCAL key_beep_on(void);
void TH04_PASCAL key_beep_off(void);
int TH04_PASCAL key_sense(int keygroup);

unsigned TH04_PASCAL key_sense_bios(void);
// --------

// Heap
// ----

void TH04_PASCAL mem_assign(unsigned top_seg, unsigned parasize);
void TH04_PASCAL mem_assign_all(void);
int TH04_PASCAL mem_unassign(void);
int TH04_PASCAL mem_assign_dos(unsigned parasize);

// Regular
void __seg* TH04_PASCAL hmem_alloc(unsigned parasize);
void __seg* TH04_PASCAL hmem_allocbyte(unsigned bytesize);
void TH04_PASCAL hmem_free(void __seg* memseg);
// Fast
void __seg* TH04_PASCAL smem_wget(unsigned bytesize);
void TH04_PASCAL smem_release(void __seg* memseg);
// ----

// Machine identification
// ----------------------

extern const unsigned __cdecl Machine_State;

unsigned TH04_PASCAL get_machine(void);

#define PC_AT        	0x0010
#define PC9801       	0x0020
#define FMR          	0x0080	/* 0.23追加 */
#define DOSBOX       	0x8000	/* 0.22k追加 */

#define DESKTOP      	0x0001
#define EPSON        	0x0002
#define PC_MATE      	0x0004
#define HIRESO       	0x0008

#define LANG_US      	0x0001
#define PC_TYPE_MASK 	0x000e
#define PS55         	0x0000
#define DOSV         	0x0002
#define PC_AX        	0x0004
#define J3100        	0x0006
#define DR_DOS       	0x0008
#define MSDOSV       	0x000a
#define VTEXT        	0x0240	/* 0.23追加 */
#define DOSVEXTENTION	0x0040	/* 0.22d追加 */
#define SUPERDRIVERS 	0x0200	/* 0.23追加 */
#define ANSISYS      	0x0100	/* 0.22d追加 */
// ----------------------

// Math
// ----

extern const short __cdecl SinTable8[256], CosTable8[256];
extern long __cdecl random_seed;

#define Sin8(t) SinTable8[(t) & 0xff]
#define Cos8(t) CosTable8[(t) & 0xff]

int TH04_PASCAL iatan2(int y, int x);
int TH04_PASCAL isqrt(long x);
int TH04_PASCAL ihypot(int x, int y);

#define irand_init(seed) \
	(random_seed = (seed))
int TH04_PASCAL irand(void);
// ----

// Optionally buffered single-file I/O
// -----------------------------------

#define SEEK_CUR    1
#define SEEK_END    2
#define SEEK_SET    0

int TH04_PASCAL file_ropen(const char TH04_PTR *filename);
int TH04_PASCAL file_read(void far *buf, unsigned wsize);
long TH04_PASCAL file_size(void);
int TH04_PASCAL file_create(const char TH04_PTR *filename);
int TH04_PASCAL file_append(const char TH04_PTR *filename);
int TH04_PASCAL file_write(const void far *buf, unsigned wsize);
void TH04_PASCAL file_seek(long pos, int dir);
void TH04_PASCAL file_close(void);
int TH04_PASCAL file_exist(const char TH04_PTR *filename);
int TH04_PASCAL file_delete(const char TH04_PTR *filename);
// -----------------------------------

// Packfiles
// ---------

extern unsigned char __cdecl pfkey; // 復号化キー
extern unsigned __cdecl bbufsiz;    // バッファサイズ

void TH04_PASCAL pfstart(const unsigned char TH04_PTR *parfile);
void TH04_PASCAL pfend(void);
#define pfsetbufsiz(bufsiz) \
	bbufsiz = bufsiz;
// ---------

// Resident data
// -------------

void __seg* TH04_PASCAL resdata_exist(
      const char TH04_PTR *id, unsigned idlen, unsigned parasize
);
void __seg* TH04_PASCAL resdata_create(
      const char TH04_PTR *id, unsigned idlen, unsigned parasize
);

#define resdata_free(seg) \
	dos_free(seg)
// -------------

// Resident palettes
// -----------------

int TH04_PASCAL respal_exist(void);
int TH04_PASCAL respal_create(void);
void TH04_PASCAL respal_get_palettes(void);
void TH04_PASCAL respal_set_palettes(void);
void TH04_PASCAL respal_free(void);
// -----------------

// VSync
// -----

// Incremented by 1 on every VSync interrupt. Can be manually reset to 0 to
// simplify frame delay loops.
extern volatile unsigned int __cdecl vsync_Count1, vsync_Count2;

#define vsync_proc_set(proc) { \
	extern func_t __cdecl vsync_Proc; \
	disable(); \
	vsync_Proc = proc; \
	enable(); \
}
#define vsync_proc_reset() { \
	extern func_t __cdecl vsync_Proc; \
	disable(); \
	vsync_Proc = nullptr; \
	enable(); \
}

void TH04_PASCAL vsync_start(void);
void TH04_PASCAL vsync_end(void);
void TH04_PASCAL vsync_wait(void);
// -----
#ifdef __cplusplus
}
#endif
/// ----------------------------------------------------------------------

/// Inlined extensions
/// ------------------

#ifdef __cplusplus
// Type-safe hmem_* memory allocation
template<class T> struct HMem {
	static T __seg* alloc(unsigned int size_in_elements) {
		return reinterpret_cast<T __seg *>(hmem_allocbyte(
			size_in_elements * sizeof(T)
		));
	}

	static void free(T far *&block) {
		hmem_free(reinterpret_cast<void __seg *>(block));
	}

	static void free(T __seg *&block) {
		hmem_free(reinterpret_cast<void __seg *>(block));
	}
};

// Type-safe resident structure allocation and retrieval
template <class T> struct ResData {
	static unsigned int id_len() {
		return (sizeof(reinterpret_cast<T *>(0)->id) - 1);
	}

	static T __seg* create(const char TH04_PTR *id) {
		return reinterpret_cast<T __seg *>(resdata_create(
			id, id_len(), ((sizeof(T) + 0xF) >> 4)
		));
	}

	static T __seg* exist(const char TH04_PTR *id) {
		return reinterpret_cast<T __seg *>(resdata_exist(
			id, id_len(), ((sizeof(T) + 0xF) >> 4)
		));
	}

	// Workarounds for correct code generation
	static T __seg* create_with_id_from_pointer(const char *&id) {
		return reinterpret_cast<T __seg *>(resdata_create(
			id, id_len(), ((sizeof(T) + 0xF) >> 4)
		));
	}

	static T __seg* exist_with_id_from_pointer(const char *&id) {
		return reinterpret_cast<T __seg *>(resdata_exist(
			id, id_len(), ((sizeof(T) + 0xF) >> 4)
		));
	}
};

inline func_t vsync_proc_get(void) {
	extern func_t __cdecl vsync_Proc;
	return vsync_Proc;
}
#endif
/// ------------------

#endif /* MASTER_HPP */

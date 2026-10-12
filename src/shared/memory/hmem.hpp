#ifndef TH04_HMEM_HPP
#define TH04_HMEM_HPP

// The TH04 call sites pass one 16-bit word and receive a segment in AX.
// Entries use the far Pascal interface of the pinned master.lib ABI.
extern "C" {
void __seg * far pascal hmem_allocbyte(unsigned int bytesize);
void far pascal hmem_free(void __seg *memseg);
unsigned long far pascal th04_smem_wget_core(unsigned bytesize);
void far pascal smem_release(void __seg *memseg);
extern unsigned __cdecl mem_Reserve;
}

#endif

#ifndef TH04_HMEM_HPP
#define TH04_HMEM_HPP

// The TH04 call sites pass one 16-bit word and receive a segment in AX.
// Both functions are far Pascal entries in the pinned master.lib ABI.
extern "C" {
void __seg * far pascal hmem_allocbyte(unsigned int bytesize);
void far pascal hmem_free(void __seg *memseg);
}

#endif

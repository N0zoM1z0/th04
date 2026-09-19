#ifndef TH04_SHARED_PLATFORM_ABI_HPP
#define TH04_SHARED_PLATFORM_ABI_HPP

// TH04 target memory-model declarations
// ------------------------

#if !defined(TH04_NEAR) && !defined(TH04_FAR) && !defined(TH04_COMPACT) && !defined(TH04_MEDIUM)
#if defined(__SMALL__) || defined(__TINY__) || defined(M_I86SM) || defined(M_I86TM)
#define TH04_NEAR
#elif defined(__COMPACT__) || defined(M_I86CM)
#define TH04_COMPACT
#elif defined(__MEDIUM__) || defined(M_I86MM)
#define TH04_MEDIUM
#elif defined(__LARGE__) || defined(__HUGE__) || defined(M_I86LM) || defined(M_I86HM)
#define TH04_FAR
#endif
#endif

#if defined(TH04_NEAR)
#define TH04_PASCAL near pascal
#define TH04_CDECL near cdecl
#define TH04_PTR near
#elif defined(TH04_FAR)
#define TH04_PASCAL far pascal
#define TH04_CDECL far cdecl
#define TH04_PTR far
#elif defined(TH04_COMPACT)
#define TH04_PASCAL near pascal
#define TH04_CDECL near cdecl
#define TH04_PTR far
#elif defined(TH04_MEDIUM)
#define TH04_PASCAL far pascal
#define TH04_CDECL far cdecl
#define TH04_PTR near
#endif

#ifndef TH04_PASCAL
#error Memory model for master.lib could not be determined?
#endif

#endif

# TH04 randring modulo helpers v388

## Scope

This packet closes the two formerly provisional 25-byte helpers
`randring1_next16_mod(unsigned int)` at load `0xBC94` and
`randring2_next16_mod(unsigned int)` at load `0x13D76`.

They are accepted on the repository's separate original-style ASM plane and do
not increase the reviewed authored C/C++ denominator.

## Producer provenance

ReC98 commit `4b8baf14` is titled
`[Reverse-engineering] [th02/th03/th04/th05] Random number ring buffer`
and introduces one low-level `RANDRING_NEXT_DEF` family across the four
games. TH05 directly includes the TH04 randring-next macro source.

An independently attested TH05 MAIN target contains exactly two matching
25-byte modulo bodies, at load `0xC724` and `0x152C0`. Their
instruction skeleton matches TH04: load the ring word, advance the byte cursor,
clear DX, load the Pascal divisor through `SS:[SP+2]`, divide, return the
remainder in AX, and `RET 2`. Only linked randring storage addresses
differ.

## Natural-C++ negative control

A bounded TC4J stack-peek implementation reaches the exact 25-byte size, but
the compiler orders `MOV BX,SP` before its implicit `XOR DX,DX`.
The target orders those instructions the other way around. Explicit
pseudo-register DX zeroing produces a duplicate XOR or extra address arithmetic
and grows the body to 27 or 31 bytes.

## Maintained symbolic source and physical layout

The maintained sources are:

- `src/main/math/randring1_next16_mod.asm`
- `src/main/math/randring2_next16_mod.asm`

Both keep `_randring` and `_randring_p` as external symbols and
express the operation symbolically. No target address or machine-byte array is
embedded.

The r1 object contributes `0x1A` physical bytes because the historical
macro is followed by source-owned `EVEN`/NOP. The logical function credit
is only the first `0x19` bytes. The r2 object likewise contributes
`0x1A` physical bytes because the historical TH04 source explicitly
places `db 0` after `RANDRING_NEXT_DEF 2`; again only the first
`0x19` bytes receive function credit.

## Replay proof

Focused staged replay `gpt-web-randring-mod-v388-focused-002` passes
twice with `failures=[]`; receipt SHA-256 is
`4354a5a10f27de21a733f13d2dbc049b19ea79d1517a64a8cabf7107593db31f`.

Both logical owners have target-identical 25-byte raw slices, exact MAP
placement inside their `0x1A` physical contributions, empty ordered
relocation overlaps, and valid deterministic TASM OMF.

Candidate aggregate
`gpt-web-randring-mod-v388-aggregate-candidate-001` passes all 263 default
owners twice. After promotion, independent final aggregate
`gpt-web-randring-mod-v388-aggregate-final-001` again passes all 263
owners twice with `failures=[]`; final receipt SHA-256 is
`a063756e427f5c2faba4275f1307f64eac5ea1494bb16f49604375b774977fc3`.

The two boundary observations now live on the `original-asm / attest-asm`
plane. They are removed from the authored-C/C++ provisional queue without
changing the C/C++ exact denominator.

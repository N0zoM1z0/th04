# MAINE sound-effect function boundaries (v699)

The MAINE sound-effect pair previously had zero-length provisional entries
because the Ghidra inventory does not create functions at either TLINK public.

Target-first review now closes the physical owners without granting exact
source credit.

- The historical th04/snd_se.cpp SHARED contribution is 0x86 bytes at
  loaded 0CC7:0930..09B5.
- SND_SE_PLAY occupies payload 0xD5A0..0xD5D8, size 0x39 (57) bytes, ending
  in RETF 2.
- Payload 0xD5D9 is one NOP of compiler/module padding and belongs to neither
  function.
- _snd_se_update occupies payload 0xD5DA..0xD625, size 0x4C (76) bytes,
  ending in RETF.
- The next SHARED contribution, th04/bgimage.cpp, starts at loaded 0CC7:09B6
  / payload 0xD626.

The retained historical snd_se.obj identifies TC86 Borland C++ 4.02 and its
linked 0x86-byte module is raw-equal to the restored target. This corroborates
layout and ownership only. The historical candidate uses pseudo-register
forcing to obtain target code shape, so no decoded-exact source credit is
claimed here.

Receipt:
.analysis/reconstruction/probes/v699-maine-snd-se-boundaries/receipt.json

Receipt SHA-256:
6c24bd1f52bac073651ccedb16fe6e77f783e97abc7da8debb137fca0b117ed4

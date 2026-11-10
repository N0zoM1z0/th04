# TH04 MAINE regist_menu ordinary-C++ closure (v835)

v835 promotes the final 924-byte MAINE authored blocker, `regist_menu()` at
payload `0xC814`.

v831 had shown a split compiler frontier: `switch` preserved the target
JZ+JMP topology but emitted MOV/OR, while direct if/goto emitted the target
memory CMP but allowed TC4.02 to fold the redundant JMP.

v835 materially expands the pinned compiler surface. The maintained source uses
an ordinary semantic conditional expression:

```cpp
(key_det != INPUT_NONE) ? input_locked : (input_locked = INPUT_NONE);
```

For nonzero input this preserves the existing lock; once input returns to
`INPUT_NONE`, it clears the lock. TC4.02 naturally emits the target
CMP/JZ/JMP topology. No `optimization_barrier`, asm, emitted bytes, register
forcing, codestring, or post-build patch is used.

Two cold builds reproduce the complete `0xB30` SCORE CODE and all 924
`regist_menu` bytes. Final MAINE EXE/MAP state and all 559 ordered relocations
remain stable under the already accepted v834 SCORE-object policy.

Canonical replay checks all 72 MAINE accepted slices raw-zero. This establishes
decoded-function exactness without claiming literal original-source spelling
or packed-file exactness.

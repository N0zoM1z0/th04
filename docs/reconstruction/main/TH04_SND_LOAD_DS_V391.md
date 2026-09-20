# TH04 snd_load DS preservation v391

## Scope

This packet promotes only two formerly blocked bytes inside the reviewed 234-byte `snd_load()` body:

- file `0x14D4E`: `PUSH DS`;
- file `0x14D76`: `POP DS`.

The adjacent two-byte `MOV BX,AX` at file `0x14D57` remains blocked and receives no credit.

## Provenance split

The DS pair has independent cross-game target corroboration. TH02, TH04, and TH05 all preserve caller DS across a song-buffer read path in which the active DS is repointed before DOS function 3Fh and restored afterward.

This does **not** extend to the handle copy. TH04 uses `89 C3`; the homologous TH02 and TH05 loaders use `8B D8`. v391 therefore treats the two claims separately.

The maintained fragments are:

- `src/shared/sound/load_push_ds.inl`
- `src/shared/sound/load_pop_ds.inl`

Each fragment uniquely matches the pinned TH04 scaffold. No byte directive, OMF patch, or target address is embedded.

## Replay proof

Focused replay `gpt-web-snd-load-ds-v391-focused-002` passes twice with `failures=[]`; receipt SHA-256 is `dd033cb2972a7b9c17b5101d3221818e4f65a88362e0dd38e06a13b58d9b23da`.

Both one-byte owners are raw/MAP/ordered-relocation exact inside the same valid TC86 `snd_load.obj`. The shared normalized object SHA-256 is `f4398c934b53f985d8e1a46721642ae4451a12f18cb4b0594728cd6719f4ff51`.

Candidate aggregate `gpt-web-snd-load-ds-v391-aggregate-candidate-001` passes the complete default cohort twice. After promotion, final aggregate `gpt-web-snd-load-ds-v391-aggregate-final-001` again passes **266/266** owners twice with `failures=[]`; receipt SHA-256 is `d55f438321b2cb31b7aae05390e8fb74d031f047e64bc51f3750b75a8eba398b`.

After this packet, `snd_load()` is **232/234 bytes exact**. Only `89 C3` remains unresolved.

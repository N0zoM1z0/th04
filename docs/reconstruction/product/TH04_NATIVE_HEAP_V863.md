# TH04 native segmented heap

2026-09-27 product-build investigation. `src/shared/memory/heap.cpp` owns
`MEM_ASSIGN`, `MEM_ASSIGN_ALL`, `MEM_ASSIGN_DOS`, `MEM_UNASSIGN`, `HMEM_ALLOC`,
`HMEM_ALLOCBYTE`, and `HMEM_FREE` in TH04 source. The public entries use the
large-model far Pascal ABI declared in `src/shared/runtime/api.hpp`. A DOS
allocation binds a descending paragraph heap. Each block has a one-paragraph
header; the public handle is its data segment. Free blocks are reused and
split when enough paragraphs remain; adjacent free blocks coalesce. Explicit
`MEM_ASSIGN_DOS` is used by MAINE initialization. `MEM_ASSIGN_ALL` and an
unassigned `HMEM_ALLOC` can allocate the available DOS block with a 256-paragraph
reserve. This is TH04-owned source informed by the bounded historical
`memheap.asm`/`mem_assign*.asm` interfaces, not a byte-exact reconstruction of
that library.

## Compiler and runtime counterexample

The first implementation returned `current + 1` directly from the free-hole
branch and `new_top + 1` from the fresh-allocation branch. Pinned TC4J 4.02J
merged the returns into one increment but also emitted an increment before
the hole branch reached that epilogue. The DOS test observed data segment
`B+1` after freeing block `B`, despite the block header being marked used at
`B-1`. The v1d private runtime receipt is
`9ac71e44ea4ae7963d9a6da1c49b91a2c148a661fd30e4a5fa04eca1fbb077d7`
(`HEAP_FAIL_4`, exit 4). Disassembly of the generated code places a `LEA
AX,[SI+1]` on the reuse branch before the shared `INC AX` epilogue. This is a
compiler-observed source-shape hazard; it is not a target observation.

The source now stores either selected header in `allocated_header` and has
one successful `return allocated_header + 1`. The checked-in
`scripts/probes/probe_th04_native_heap_runtime.py` compiles this owner with
TC4J, links with pinned Borland system libraries, and runs under pinned
MS-DOS Player. The v3 run (receipt
`971aaf0f16e5c4590d1adc5411419a4162845960a8deb160820d96fe320b2d64`)
exits 0 with `HEAP_PASS`. It checks DOS assignment, distinct segment handles,
far memory writes, hole reuse, split-tail reuse, free coalescing, duplicate
free, an 8,000-byte allocation, unassignment, and re-assignment. This is a DOS
runtime observation of the isolated allocator, not a PC-98 MAINE scenario.

## Product build and static checks

Two cold no-archive MAINE builds compile 119 TH04 units (77 C++, 42 ASM),
leave 18 unresolved names, and report zero warnings. Link-relevant and
timestamp-normalized OMF records agree for all objects; only BGIMAGE has its
known raw timestamp drift. Receipt SHA-256 values are
`9aeed0e7894df94461d3745941d7ccad0a51403358bee1ba0cfcb615771ea44b`
and `2a84263c455fc586429bd51c76f193b11ad50636fa95856ea7a7baa08a0b3dc9`.
The manifest digest is
`ae85d72bd0ad657e495f0239541664f51e3844d3035450122f23e2bd3260e9ce`.

The historical-library calibration TLINK exits 0 (receipt
`95ba6f31adabf106079e42e8896023125fc77a7f1b50d5f9e34f010ff38c64fc`)
with the known archive-dictionary warning. Its MZ validates 604 relocation
sites at two DOS load segments (receipt
`f0698b498fb30191569d9202a3143bbc47df53e9781a0f0d62ecdf032f1ee9ad`).
The call audit checks 27 far entry return ABIs, 107 relocated direct far
calls, and one same-CS `push cs; call` (receipt
`e96c2bbf6a5fe38d50083ed201ac5af87fe8de1d8b68eb0a0c184447a5afb391`).
At calibration MAP `096C:36B4` through `096C:37A1`, the seven heap entries
have `RETF 4`, `RETF`, `RETF 2`, `RETF`, `RETF 2`, `RETF 2`, and `RETF 2`
respectively. `HMEM_ALLOC`, `MEM_ASSIGN`, and `MEM_ASSIGN_ALL` have no MAINE
call site; only their entry return ABI was checked. Calibration addresses are
not original target addresses.

The calibration MZ still contains historical support and has not reached
MAINE under PC-98 runtime. Available-block DOS failure and memory pressure
remain untested; allocator success does not prove page-copy behavior or target
byte identity. The remaining no-archive symbols are text gaiji (3), VSYNC
(3), sprites (3), sound (4), packed-file service (3), and packed graphics
(2). This bounded runtime probe catches a failure that static OMF, TLINK,
relocation, and return checks all missed; repeat it for TH05 when adapting a
segmented allocator.

Replay with fresh private output directories:

```bash
python3 scripts/probes/probe_th04_native_heap_runtime.py --output-dir .analysis/reconstruction/probes/heap-replay
python3 scripts/probes/probe_th04_native_maine_link.py --without-support --output-dir .analysis/reconstruction/probes/maine-heap-a
python3 scripts/probes/probe_th04_native_maine_link.py --without-support --output-dir .analysis/reconstruction/probes/maine-heap-b
python3 scripts/probes/compare_th04_native_maine_link.py .analysis/reconstruction/probes/maine-heap-a .analysis/reconstruction/probes/maine-heap-b
python3 scripts/probes/probe_th04_native_maine_link.py --output-dir .analysis/reconstruction/probes/maine-heap-lib
python3 scripts/probes/audit_th04_native_maine_mz.py --link-receipt .analysis/reconstruction/probes/maine-heap-lib/receipt.json --output-dir .analysis/reconstruction/probes/maine-heap-mz
python3 scripts/probes/audit_th04_native_maine_call_abi.py --link-receipt .analysis/reconstruction/probes/maine-heap-lib/receipt.json --output-dir .analysis/reconstruction/probes/maine-heap-call
```

## Semantic preservation on semantic/readable

The 2026-10-03 pass names header segments, the exclusive region sentinel,
the lowest linked block, first-fit hole reuse, paragraph counts and DOS
ownership in `src/shared/memory/heap.cpp`. Comments distinguish the six-byte
header struct from its reserved 16-byte paragraph, explain the minimum useful
split, both-neighbor coalescing and reclamation of the leading free prefix.
Public names, far Pascal signatures, declaration order and expression order
are retained. The single successful allocation return is retained because of
the previously reproduced TC4J double-increment counterexample.

`MEM_ASSIGN` binds caller-owned memory and does not reject rebinding;
`MEM_ASSIGN_DOS` rejects a bound/empty region with -8. `MEM_UNASSIGN` clears
local ownership before DOS release, including when that release fails. A free
requires the exact payload segment; the reserved header ID is always zero,
so a stale handle can alias a later allocation at the same segment. These
are source contracts to consider explicitly in a native port, not changes
made by the readability pass.

Dependency-validated fast build `product-20261003-040353-7d7e1b7e` preserves
all complete MAIN/OP/MAINE bytes and ordered relocations against the preceding
BFNT batch: 192,351/77,740/70,614 bytes, 1,178/814/660 relocation entries,
SHA-256 `dbbfa404…`, `c8ac4d73…`, `0a2d3ce8…`. Comparator receipts:
`.analysis/ARTIFACT.EXE.semantic-heap-compare.json`.

The existing independent DOS lifecycle harness returns `HEAP_PASS`, checking
assignment, distinct handles and writes, exact reuse of a freed handle, split
tail reuse, coalescing/duplicate free, an 8,000-byte allocation and reassignment.
Receipt: `.analysis/reconstruction/probes/semantic-heap-runtime-20261003/receipt.json`.
This is source-to-source compiler preservation plus bounded allocator runtime
coverage. It is not original library byte equality or a PC-98 ending replay.

```text
python3 scripts/build.py --only main op maine --output-dir .analysis/build/semantic-heap-readable --main-cpp-cache .analysis/reconstruction/probes/product-20261003-035054-8c7fc31c-main --op-cache .analysis/reconstruction/probes/product-20261003-035054-8c7fc31c-op --maine-cache .analysis/reconstruction/probes/product-20261003-035054-8c7fc31c-maine --progress
python3 scripts/compare_artifacts.py .analysis/build/semantic-super-readable/MAIN.EXE .analysis/build/semantic-heap-readable/MAIN.EXE --json
python3 scripts/probes/probe_th04_native_heap_runtime.py --output-dir .analysis/reconstruction/probes/semantic-heap-runtime-20261003
```

Repeat the complete comparator for OP and MAINE.

# TH04 native x64 port

Current products, verified behavior and blockers are in
[the handoff](RE_HANDOFF.md). Build and runtime options are in
[PORTABLE.md](PORTABLE.md); original-data preparation is in
[PREPARE_DATA.md](PREPARE_DATA.md).

`port64/` contains the maintained C++17 game and component checks. Build the
actual game target instead of compiling every historical test program:

```sh
cmake -S port64 -B .analysis/port64/build -DCMAKE_BUILD_TYPE=Release
cmake --build .analysis/port64/build --target th04-port64 --parallel 1
```

Select contract programs and runtime comparisons for the changed subsystem.
Use fresh output when old objects have been removed. Keep game data and saves
outside disposable build directories.

The unresolved original DOS timing and physical input questions are summarized
in [the comparison note](reconstruction/product/TH04_REPLAY_DIFFERENTIAL.md).
Native host agreement and logical clears do not establish original timing
parity. Exact state remains in the reconstruction ledgers.

`python3 scripts/ci.py` checks the complete source tree without private inputs.
It does not build the game or launch a window. Preserve muted, isolated runtime
tests and keep the user's active desktop undisturbed.

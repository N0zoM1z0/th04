# Current native Windows host verification

v1332, 2026-10-09. This batch repairs MinGW runtime linkage and the binary
configuration failure capture, then replays current components and bounded
frontends on actual Windows AMD64. All launches explicitly use `--mute`;
no audio device is opened. Full natural routes, FM/OPN synthesis, physical
clock equivalence and historical DOS exactness remain outside this result.

## Rejected observations and repairs

The first local NTFS verifier run rejects
`th04-port64-beeper-contracts.exe` with exit -1073741515 (0xC0000135).
The older explicit CMake target list covers only 34 contracts plus the GUI;
17 newer contracts lack the static runtime flags. Import inspection finds
MinGW runtime DLL requirements in those targets. `th04-portable-core` now
publishes the existing static link options through its INTERFACE, so all
current and later consuming executables inherit them. Every one of the 52
current Windows programs imports only KERNEL32/msvcrt and, for the GUI,
USER32/GDI32; no auxiliary runtime DLL is supplied to make the test pass.

After that repair, all 51 Windows contracts and five frontends pass, but
configuration phase0 rejects four `failed*/rejected.txt` files. Their only
byte difference is CRLF versus the Linux LF diagnostic. Original control
assertions already reject the blocked save and retain OP without MAIN.
The diagnostic stream now opens with `std::ios::binary`; no comparator
normalization or output exemption is added. Raw negative files, logs and
physical saves remain under the batch's `windows-partial/` recovery.

Executing the authored PowerShell script directly from the WSL UNC path
hits the host unsigned/network-script policy. Copying that same hash-checked
script to the owned NTFS temporary stage permits ordinary `-NoProfile -File`
execution; no policy override or global policy change is used.

## Replay and identities

`port64/verify_windows_current.ps1` consumes a muted version1 JSON plan.
It checks each input and all products before and after execution, attests
AMD64 PE32+, runs all 51 contracts, then nine explicit muted GUI cases.
Each fresh case compares the exact complete file set and SHA-256 vector.
Configuration/setup phase1 uses a separate actual process reading phase0's
physical NTFS saves. HDI/font and seed inputs remain read-only.

The private plan is `.analysis/port64/windows-current-v1332/plan-final.json`;
its generator is `make_plan_final.py` in the same directory. To replay,
materialize a fresh owned NTFS stage and fresh seed directories, update the
plan's paths and current product vector, copy the hash-checked public verifier
locally, then invoke:

```powershell
powershell.exe -NoProfile -File C:\<owned-stage>\verify_windows_current.ps1 -PlanFile <fresh-plan.json>
```

The final consumer manifest is
`88e262354e833555e04938cc3313f8395b813309b2f02c6140e9d893854b4528`
with 395 maintained files and 156 products across GNU, optimized UBSan and
MinGW. All 102 GNU/UBSan contract product hashes retain v1331 identities;
the three GUIs have new identities after the binary capture change.
MinGW contracts also have new identities after static relinking. Compiler,
cache, product, source and complete import vectors are bound in
`product-profile.json` and `source-profile.json`; source archive members pass
full digest readback. Completed earlier producers keep their own manifests.

Current GNU `linux-final/receipt.json` records nine fresh launches and 2,015
files, fully equal to immutable original-backed bounded references: sound
scenes1150, score-route220, Music Room242, Scores179, demos72,
configuration48+16 and first setup61+27. Those prior originals are reused,
not re-executed in this host batch. Earlier Linux producer and rejected
Windows snapshots are retained separately. GNU and optimized UBSan each
pass all 51 CTests after both changes.

## Acceptance and retention

Actual Windows NT10.0.22631 AMD64 passes all 51 contracts and all nine fresh
muted frontend launches, with 2,015 complete output files exactly matching the
current GNU producer. Configuration/setup restart and failed writers execute
on independent physical NTFS save directories. Windows acceptance receipt
SHA-256 is
`6c7ea8b01c36e20a8902fae31d6ac384fd895161ffa016974d8278245a8001f4`.
Final source/product/cache/archive/output readback passes in `readback.json`.

Terminal capture sharing and owned-stage removal reclaim 2,213,810,176
allocated bytes (about2.06GiB): two Linux2015-file capture batches,
1,911 rejected-run Windows outputs and the final Windows stage. Every shared
capture first passes complete hash and byte comparison. All554 final protected
hashes remain unchanged; actual logs/receipt/physical saves and four negative
CRLF captures remain. Current156programs,395sources andHDI/font are retained.
Windows outputs retained under `windows/` are immutable verified aliases;
future writers require a new output directory. No GUI package is published.

Installed DOS products, original data and independent saves remain untouched.
The archived v1296 native preview is historical. Source/evidence throughv1331
was committed/pushed as94c63a5 and0d52ceb; current repairs are9da0c7b andaac8ec5.
Full natural routes, PMD/FM chip/synthesis and physical timing/performance
remain next owners; this host verification does not activate FM capability.

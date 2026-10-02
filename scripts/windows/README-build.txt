TH04 Reconstruction: Windows Source Build

Open Command Prompt in this folder and run:

    build-th04.cmd

The command uses WSL and the attested 16-bit toolchain to compile changed
source, verify cached objects, relink three EXEs, and audit the output. An
unchanged, previously audited ZUN.COM is reused; changed ZUN inputs trigger a
fresh source build. Its progress bars count generated or verified objects and
completed ZUN source/packing passes. It then verifies executable hashes and
refreshes play.hdi while retaining the saved game files.

The build produces the invincible gameplay test variant. The original game
data supplies assets only; original executable bytes are not link inputs.

Optional commands:

    build-th04.cmd -CheckOnly
    build-th04.cmd -Launch
    build-th04.cmd -Cold

-Cold rebuilds every product from source. The first build is cold when no
verified package and build cache exist. The default incremental command is
intended for a quick, repeatable live demonstration; it prints hashes of all
four executable products.

The source checkout and pinned compiler tools must remain available in WSL.
Close DOSBox-X before building so the playable disk image can be refreshed.

Use start-th04.bat for the 24,000-cycle gameplay profile. To compare against
the collection's original 15,000-cycle setting, use
start-th04-reference.bat. Both launchers use the same saved play.hdi.

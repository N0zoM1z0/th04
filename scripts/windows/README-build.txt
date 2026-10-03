TH04 Reconstruction: Windows Source Build

Open Command Prompt in this folder and run:

    build-th04.cmd

The command uses WSL and the attested 16-bit toolchain to compile changed
source, verify cached objects, relink three EXEs, and audit the output. An
unchanged, previously audited ZUN.COM is reused; changed ZUN inputs trigger a
fresh source build. Its progress bars count generated or verified objects and
completed ZUN source/packing passes. It then verifies executable hashes and
refreshes play.hdi while retaining the saved game files.

The default build produces the invincible gameplay test variant. For normal
collision damage and lives, run build-th04.cmd -Normal. Both variants are
reconstructed from maintained source. The original game data supplies assets
only; original executable bytes are not link inputs.

Optional commands:

    build-th04.cmd -CheckOnly
    build-th04.cmd -Launch
    build-th04.cmd -Cold
    build-th04.cmd -Normal
    build-th04.cmd -Normal -Launch

-Cold rebuilds every product from source. The first build is cold when no
verified package and build cache exist. The default incremental command is
intended for a quick, repeatable live demonstration; it prints hashes of all
four executable products.

The source checkout and pinned compiler tools must remain available in WSL.
Close DOSBox-X before building so the playable disk image can be refreshed.

Use start-th04.bat for the 24,000-cycle gameplay profile. To compare against
the collection's original 15,000-cycle setting, use
start-th04-reference.bat. Both launchers use the same saved play.hdi.

Use start-th04-normal.bat for normal gameplay at 24,000 cycles. It mounts
play-normal.hdi, with separate saves. Its first export copies the existing
play.hdi saves; subsequent builds preserve each variant's own saves.
Invincibility is compiled into the test MAIN.EXE using a private build-time
source overlay. The normal MAIN.EXE has no such overlay; launchers do not
patch memory or modify executables at runtime.

For dense-bullet CPU headroom, try start-th04-normal-highcpu.bat (normal) or
start-th04-highcpu.bat (invincible). These use the same respective disk images
and saves at 36,000 cycles; they do not enable fast-forward or change game code.
Close any existing TH04 instance first. The standard launchers remain at
24,000 cycles. More host CPU cores cannot parallelize DOSBox-X's guest CPU;
the dynamic core and sufficient fixed cycles matter. A higher cycle setting
needs Windows gameplay/audio testing and may not help when the host is busy.

// Private DOSBox-X CPU observer. No guest writes or exception suppression.
static void th04_cpu_fault_observe(Bitu which) {
    const char *directory = getenv("TH04_CPU_FAULT_DIR");
    static unsigned int count = 0;
    if (!directory || (which != 0 && which != 6) || count >= 32) return;
    const unsigned int id = count++;
    fprintf(stderr,
        "TH04_CPUFAULT %u %02X %04X %04X %04X %04X %04X %04X "
        "%04X %04X %04X %04X %04X %04X %04X %08X\n",
        id, (unsigned int)which, (unsigned int)SegValue(cs),
        (unsigned int)(reg_eip & 0xffff), (unsigned int)SegValue(ss),
        (unsigned int)reg_sp, (unsigned int)SegValue(ds), (unsigned int)SegValue(es),
        (unsigned int)reg_ax, (unsigned int)reg_bx, (unsigned int)reg_cx,
        (unsigned int)reg_dx, (unsigned int)reg_si, (unsigned int)reg_di,
        (unsigned int)reg_bp, (unsigned int)reg_flags);
    // reg_flags may still contain lazy flags; this prints raw emulator state.
    // Restrict reads to conventional RAM to avoid VRAM/device read effects.
    const char *names[] = {"code", "stack", "data"};
    const unsigned long starts[] = {
        (unsigned long)SegPhys(cs) + (reg_eip & 0xffff),
        (unsigned long)SegPhys(ss) + reg_sp,
        (unsigned long)SegPhys(ds)
    };
    const unsigned long sizes[] = {64, 64, 65536};
    for (unsigned int block = 0; block < 3; ++block) {
        if (cpu.pmode || starts[block] + sizes[block] > 0xa0000) continue;
        char filename[1024];
        const int length = snprintf(filename, sizeof(filename), "%s/cpu-fault-%02u-%s.bin",
                                    directory, id, names[block]);
        if (length < 0 || (unsigned int)length >= sizeof(filename)) continue;
        FILE *file = fopen(filename, "wb");
        if (!file) continue;
        for (unsigned long offset = 0; offset < sizes[block]; ++offset)
            fputc(mem_readb((PhysPt)(starts[block] + offset)), file);
        fclose(file);
    }
    fflush(stderr);
}

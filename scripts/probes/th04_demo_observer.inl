// Read-only normal-core observer. Read host RAM directly, including VM86 page
// translation, so observation cannot set guest page-table accessed bits.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>

namespace th04_demo_observer {
struct Hook { unsigned kind, segment, offset; };
struct Field { unsigned offset, size; };
static FILE *trace = nullptr;
static unsigned data_segment, image_size, process = 0, load_segment = 0;
static bool enabled = false, active = false;
static unsigned char signature[32];
static std::vector<Hook> hooks;
static std::vector<Field> fields;
static unsigned long long lcg_count = 0, ring_count = 0;
static unsigned completed = 0, stop_after = 4;

static void fail(const char *reason) {
    fprintf(stderr, "TH04_DEMO_OBSERVER_ERROR %s\n", reason);
    fflush(stderr);
    exit(91);
}
static unsigned physical_byte(unsigned address) {
    if (address >= MEM_TotalPages() * 4096u ||
        (address >= 0xa0000u && address < 0x100000u)) fail("non-RAM read");
    return MemBase[address];
}
static unsigned physical_dword(unsigned address) {
    unsigned value = 0;
    for (unsigned i = 0; i < 4; ++i) value |= physical_byte(address+i) << (i*8);
    return value;
}
static unsigned byte(unsigned linear) {
    if (linear >= 0xa0000u) fail("non-conventional logical read");
    unsigned physical = linear;
    if (cpu.cr0 & 0x80000000u) {
        if (cpu.cr4 & 0x20u) fail("PAE unsupported");
        unsigned directory = physical_dword((paging.cr3 & 0xfffff000u) + (linear >> 22)*4);
        if (!(directory & 1u)) fail("page directory absent");
        if (directory & 0x80u) physical = (directory & 0xffc00000u) + (linear & 0x3fffffu);
        else {
            unsigned page = physical_dword((directory & 0xfffff000u) + ((linear >> 12)&1023u)*4);
            if (!(page & 1u)) fail("page absent");
            physical = (page & 0xfffff000u) + (linear & 4095u);
        }
    }
    return physical_byte(physical);
}
static unsigned word(unsigned linear) { return byte(linear) | (byte(linear+1)<<8); }
static void hex(unsigned linear, unsigned size) {
    for (unsigned i = 0; i < size; ++i) fprintf(trace, "%02x", byte(linear+i));
}
static void init() {
    const char *profile = getenv("TH04_DEMO_PROFILE");
    const char *output = getenv("TH04_DEMO_TRACE");
    if (!profile && !output) return;
    if (!profile || !output) fail("incomplete observer configuration");
    FILE *input = fopen(profile, "r");
    if (!input) fail("profile open");
    unsigned count;
    if (fscanf(input, "%x %x", &data_segment, &image_size) != 2) fail("profile header");
    for (unsigned i = 0; i < 32; ++i) {
        unsigned value;
        if (fscanf(input, "%2x", &value) != 1) fail("profile signature");
        signature[i] = (unsigned char)value;
    }
    if (fscanf(input, "%u", &count) != 1 || count > 32) fail("hook count");
    while (count--) {
        Hook hook;
        if (fscanf(input, "%u %x %x", &hook.kind, &hook.segment, &hook.offset) != 3)
            fail("hook record");
        hooks.push_back(hook);
    }
    if (fscanf(input, "%u", &count) != 1 || count > 64) fail("field count");
    while (count--) {
        Field field;
        if (fscanf(input, "%x %u", &field.offset, &field.size) != 2 ||
            field.offset+field.size > 65536u || field.size > 256) fail("field record");
        fields.push_back(field);
    }
    fclose(input);
    trace = fopen(output, "wx");
    if (!trace) fail("trace open (must be fresh)");
    enabled = true;
    const char *stop = getenv("TH04_DEMO_STOP_AFTER");
    if (stop) stop_after = (unsigned)strtoul(stop, nullptr, 10);
    if (stop_after < 1 || stop_after > 4) fail("invalid demo count");
    fprintf(stderr, "TH04_DEMO_OBSERVER_ARM\n");
}
static void observe() {
    static bool initialized = false;
    if (!initialized) { initialized = true; init(); }
    if (!enabled) return;
    const unsigned ip = reg_eip & 65535u, cs_value = SegValue(cs);
    // MAIN's entry bytes are attested separately against the entire relocated
    // image emitted here. No guest bytes, registers, clocks or input are changed.
    if (ip == 0 && cs_value*16u+32u <= 0xa0000u &&
        (!cpu.pmode || (reg_flags & 0x20000u))) {
        bool match = true;
        if (word(cs_value*16+1) != ((cs_value+data_segment)&65535u)) match = false;
        for (unsigned i = 3; i < 32; ++i)
            if (byte(cs_value*16+i) != signature[i]) { match = false; break; }
        if (match) {
            active = true; load_segment = cs_value; ++process;
            lcg_count = ring_count = 0;
            fprintf(trace, "L %u %04x %08x %08x ", process, load_segment,
                    (unsigned)cpu.cr0, (unsigned)paging.cr3);
            hex(load_segment*16, image_size); fprintf(trace, "\n"); fflush(trace);
        }
    }
    if (!active) return;
    for (unsigned i = 0; i < hooks.size(); ++i) {
        const Hook &hook = hooks[i];
        if (ip != hook.offset || cs_value != load_segment+hook.segment) continue;
        if (hook.kind == 3 || hook.kind == 4) {
            if (hook.kind == 3) ++lcg_count; else ++ring_count;
            fprintf(trace, "R %u %u %04x %04x %04x %04x %04x %04x\n", process,
                    i, cs_value, ip, (unsigned)SegValue(ss), (unsigned)reg_sp,
                    word(SegBase(ss)+reg_sp), word(SegBase(ss)+reg_sp+2));
        } else {
            if (SegValue(ds) != load_segment+data_segment) fail("MAIN DGROUP mismatch");
            if (hook.kind == 2 && word(SegBase(ds)+fields[0].offset) != 3996u) continue;
            fprintf(trace, "%c %u %04x %04x %04x %llu %llu",
                    hook.kind == 1 ? 'I' : 'T', process, cs_value, ip,
                    (unsigned)SegValue(ds), lcg_count, ring_count);
            for (const Field &field : fields) {
                fprintf(trace, " "); hex(SegBase(ds)+field.offset, field.size);
            }
            // Preserve resident identity and relevant bytes separately from the
            // candidate's relocated pointer; the last field is the far pointer.
            const Field &pointer = fields.back();
            const unsigned address = SegBase(ds)+pointer.offset;
            const unsigned resident = word(address+2)*16+word(address);
            fprintf(trace, " "); hex(resident, 80); fprintf(trace, "\n"); fflush(trace);
            if (hook.kind == 2) {
                active = false;
                if (++completed == stop_after) {
                    fprintf(stderr, "TH04_DEMO_OBSERVER_COMPLETE %u\n", completed);
                    exit(0);
                }
            }
        }
        break;
    }
}
}

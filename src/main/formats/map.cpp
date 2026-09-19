#pragma option -zCEND_TEXT -zPmain_01

#include "src/shared/runtime/api.hpp"
#include "src/main/formats/map.hpp"
#include "src/shared/config/resident.hpp"

extern char *map_fn;

void near map_load(void)
{
    map_header_t mh;

    map_fn[3] = resident->stage_ascii;
    file_ropen(map_fn);
    file_read(&mh, sizeof(mh));

    map_free();
    map_seg = reinterpret_cast<map_section_tiles_t __seg *>(hmem_allocbyte(mh.size));
    file_read(map_seg, mh.size);
    file_close();
}

void near map_free(void)
{
    if(map_seg) {
        hmem_free(map_seg);
        map_seg = nullptr;
    }
}

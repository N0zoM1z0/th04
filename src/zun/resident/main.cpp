#pragma option -2

#include <stddef.h>

#include "src/zun/runtime/api.hpp"
#include "src/shared/config/resident.hpp"

extern char debug;
void cfg_init(resident_t __seg *resident_seg);

#define LOGO \
    "東方幻想郷用　 常駐プログラム　RES_HUMA.com Version1.00       (c)zun 1998"
#define ERROR_NOT_RESIDENT "わたし、まだいませんよぉ"
#define REMOVED "さよなら、また会えたらいいな"
#define INITIALIZED "それでは、よろしくお願いします"

#define arg_is(arg, capital, small) \
    (((arg[0] == '-') || (arg[0] == '/')) && \
     ((arg[1] == capital) || (arg[1] == small)))

int main(int argc, const unsigned char **argv)
{
    resident_t __seg *seg;
    const char *res_id = RES_ID;
    int i;
    uint8_t far *resident_bytes;

    seg = ResData<resident_t>::exist_with_id_from_pointer(res_id);
    dos_puts2("\n\n" LOGO "\n");
    graph_clear();

    if(argc == 2) {
        if(arg_is(argv[1], 'R', 'r')) {
            if(!seg) {
                dos_puts2(ERROR_NOT_RESIDENT "\n\n");
                return 1;
            }
            dos_free(seg);
            dos_puts2(REMOVED "\n\n");
            return 0;
        } else if(arg_is(argv[1], 'D', 'd')) {
            debug = 1;
        } else {
            dos_puts2("そんなオプション付けられても、困るんですけど\n\n");
            return 1;
        }
    }

    if(seg) {
        dos_puts2("わたし、すでにいますよぉ\n\n");
        return 1;
    }

    seg = ResData<resident_t>::create_with_id_from_pointer(res_id);
    if(!seg) {
        dos_puts2("作れません、わたしの居場所がないの！\n\n");
        return 1;
    }

    resident_bytes = reinterpret_cast<uint8_t far *>(seg);
    dos_puts2(INITIALIZED "\n\n");
    for(i = (ResData<resident_t>::id_len() + 1); i < sizeof(resident_t); i++) {
        resident_bytes[i] = 0;
    }

    cfg_init(seg);
    resident_t far *resident;
    resident = reinterpret_cast<resident_t far *>(resident_bytes);
    if(debug) {
        resident->debug = true;
    }
    return 0;
}

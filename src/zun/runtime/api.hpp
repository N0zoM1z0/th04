#ifndef TH04_ZUN_RUNTIME_API_HPP
#define TH04_ZUN_RUNTIME_API_HPP

// The retained composite wrapper still includes master.hpp for its external
// support body. Maintained ZUN translation units use these scoped declarations
// when compiled on their own.
#ifndef MASTER_HPP
typedef unsigned char bool;
typedef unsigned char uint8_t;
#define false 0
#define true 1

extern "C" {
void near pascal dos_puts2(const char near *text);
void near pascal dos_free(void __seg *segment);

int near pascal file_ropen(const char near *filename);
int near pascal file_create(const char near *filename);
int near pascal file_append(const char near *filename);
int near pascal file_read(void far *buffer, unsigned size);
int near pascal file_write(const void far *buffer, unsigned size);
void near pascal file_seek(long offset, int origin);
void near pascal file_close(void);

void __seg *near pascal resdata_exist(
    const char near *id, unsigned id_length, unsigned paragraphs
);
void __seg *near pascal resdata_create(
    const char near *id, unsigned id_length, unsigned paragraphs
);
}

template<class T> struct ResData {
    static unsigned id_len() {
        return sizeof(reinterpret_cast<T *>(0)->id) - 1;
    }

    static T __seg *exist_with_id_from_pointer(const char *&id) {
        return reinterpret_cast<T __seg *>(
            resdata_exist(id, id_len(), ((sizeof(T) + 15) >> 4))
        );
    }

    static T __seg *create_with_id_from_pointer(const char *&id) {
        return reinterpret_cast<T __seg *>(
            resdata_create(id, id_len(), ((sizeof(T) + 15) >> 4))
        );
    }
};
#endif

// The composite wrapper's master.hpp does not declare this graphics entry.
extern "C" void near pascal graph_clear(void);

#endif

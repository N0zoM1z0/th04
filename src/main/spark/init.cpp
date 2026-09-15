#pragma option -zCCIRCLE_TEXT -zPmain_01
#pragma option -k-

#include "th04/main/spark.hpp"

extern "C" unsigned char pascal far IRand(void);

extern "C" void near sparks_init(void)
{
    register spark_t near *spark;
    register int sparks_left;

    spark = sparks;
    sparks_left = SPARK_COUNT_BUG;
    do {
        // The target initializes only the low byte of the 16-bit angle field.
        *reinterpret_cast<unsigned char near *>(&spark->angle) = IRand();
        spark++;
    } while(--sparks_left != 0);

    // spark_ring_offset is 16-bit storage, but the target clears only its low
    // byte here. The add/wrap path continues to use the full 16-bit value.
    *reinterpret_cast<unsigned char near *>(&spark_ring_offset) = 0;
}

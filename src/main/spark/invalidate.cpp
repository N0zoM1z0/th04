#pragma option -zCCIRCLE_TEXT -zPmain_01
#pragma option -k-

#include "th04/main/spark.hpp"
#include "th04/main/tile/tile.hpp"
static const pixel_t SPARK_W = 8;
static const pixel_t SPARK_H = 8;

extern "C" void pascal near tiles_invalidate_around(const SPPoint center);

void near sparks_invalidate(void)
{
    *reinterpret_cast<unsigned long near *>(&tile_invalidate_box) = (
        (static_cast<unsigned long>(SPARK_W) << 16) | SPARK_H
    );

    register spark_t near *spark;
    register int sparks_left;

    sparks_left = SPARK_COUNT_BUG;
    spark = sparks;
    do {
        if(spark->flag != F_FREE) {
            tiles_invalidate_around(spark->center.prev);
        }
        spark++;
    } while(--sparks_left > 0);
}

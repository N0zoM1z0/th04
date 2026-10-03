#include "main_state.hpp"
#include "motion_tables.hpp"
#include "sprite_sheet.hpp"
#include "stage_background.hpp"
#include <fstream>
#include <iterator>
#include <iostream>
#include <stdexcept>
#include <vector>

namespace m = th04::portable::motion;
namespace p = th04::portable::player;
namespace i = th04::portable::item;
namespace a = th04::portable::application;
namespace g = th04::portable::gameplay;
namespace {
void require(bool condition, const char* reason) {
    if (!condition) throw std::runtime_error(reason);
}
void motion_contracts() {
    require(m::wrap(32768) == -32768 && m::wrap(-32769) == 32767, "16-bit motion wrap");
    require(m::floor_shift8(-257) == -2 && m::floor_shift8(-1) == -1, "negative SAR rounding");
    require(m::angle_to({}, {}) == 0, "coincident angle");
    const m::Point directions[] = {{16,0},{16,16},{0,16},{-16,16},{-16,0},{-16,-16},{0,-16},{16,-16}};
    for (unsigned n = 0; n < 8; ++n) require(m::angle_to({}, directions[n]) == n*32, "angle octant");
    for (unsigned angle = 0; angle < 256; ++angle) {
        const auto v = m::polar(static_cast<std::uint8_t>(angle), 256);
        const auto opposite = m::polar(static_cast<std::uint8_t>(angle + 128), 256);
        require(v.x == -opposite.x && v.y == -opposite.y, "polar half-turn symmetry");
    }
    p::Movement player;
    player.update(p::left, false);
    require(player.position().current.x == 188*16, "aligned movement");
    player.update(p::left | p::right, false);
    require(player.position().current.x == 192*16 && player.previous_input() == p::left,
            "new opposing key wins without changing original latch");
    player.update(p::left | p::right, false);
    require(player.position().current.x == 196*16, "conflicting held chord priority");
    player.update(p::up | p::right, true);
    require(player.position().current.x == 199*16-24 && player.position().current.y == 320*16-24,
            "diagonal shift movement");
    for (unsigned n = 0; n < 200; ++n) player.update(p::up | p::right, false);
    require(player.position().current.x == 376*16 && player.position().current.y == 8*16, "player clamp");
    require(player.position().velocity.x == 48, "clamp retains input velocity");
    p::Movement keypad;
    keypad.update(0x0400, false);
    require(keypad.position().current.x == 189*16 && keypad.position().current.y == 323*16,
            "keypad diagonal");
}
void pool_contracts() {
    i::Pool pool;
    i::ScoreState score;
    const m::Point far_player{192*16, 320*16};
    require(pool.add({100*16, 100*16}, i::Type::point), "item spawn");
    pool.update(score, far_player, false, 0);
    require(pool.entities()[0].position.current.y == 97*16 &&
            pool.entities()[0].position.velocity.y == -47 &&
            pool.entities()[0].position.previous.y == 100*16, "move before gravity");
    for (unsigned n=0; n<48; ++n) pool.update(score, far_player, false, 0);
    require(pool.entities()[0].position.current.y == 424 && pool.entities()[0].position.velocity.y == 1,
            "ballistic apex");

    i::Pool collect_pool;
    collect_pool.add({192*16, 323*16}, i::Type::power);
    auto event = collect_pool.update(score, far_player, false, 0);
    require(event.events[0].collected && score.power == 1 && score.items_collected == 1 &&
            collect_pool.entities()[0].flag == i::Flag::remove, "pickup after motion and deferred removal");
    collect_pool.update(score, far_player, false, 0);
    require(collect_pool.entities()[0].flag == i::Flag::free, "next-frame reclaim");

    i::Pool miss_pool;
    miss_pool.add({100*16, 379*16}, i::Type::dream);
    event = miss_pool.update(score, far_player, false, 0);
    require(event.events[0].missed && score.item_playperf_lower == 4, "bottom boundary miss");
    i::Pool top_pool;
    top_pool.add({100*16, -8*16}, i::Type::point);
    top_pool.update(score, far_player, false, 0);
    require(top_pool.entities()[0].position.current.y == -128, "top clamp does not remove");

    i::Pool pull_pool;
    pull_pool.add({100*16, 100*16}, i::Type::point);
    pull_pool.update(score, {200*16,100*16}, true, 0);
    require(pull_pool.entities()[0].position.current.x == 110*16 &&
            pull_pool.entities()[0].position.velocity.x == 0 &&
            pull_pool.entities()[0].position.velocity.y == 1, "pull speed and falling-half x reset");
    pull_pool.update(score, far_player, false, 0);
    require(pull_pool.entities()[0].position.current.x == 110*16 &&
            pull_pool.entities()[0].position.current.y == 100*16 &&
            !pull_pool.entities()[0].pulled_to_player, "pull cancellation stops immediately");

    i::Pool invincible_pool;
    invincible_pool.add({192*16,323*16}, i::Type::bomb);
    require(!invincible_pool.update(score,far_player,false,1).events[0].collected, "miss animation disables pickup");
    i::Pool full;
    for (unsigned n=0; n<i::pool_size; ++n) full.add({100*16,100*16},i::Type::point);
    i::EnemyDropSequence sequence(1);
    require(!full.add_enemy_drop({},sequence) && sequence.cycle() == 2 && full.spawned() == 32,
            "full pool consumes automatic drop cycle");
}
void main_contracts() {
    a::State application;
    application.start_normal(a::Playchar::reimu,a::ShotType::a);
    g::State scene(application);
    require(scene.score().power == 1 && scene.score().remaining_lives == 3, "session starting resources");
    scene.add_item({196*16,323*16},i::Type::power);
    scene.update(p::right,false);
    require(scene.score().power == 2 && scene.item_events().events[0].collected,
            "MAIN updates player before item pickup");
    const auto drops = scene.add_miss_items();
    require(drops.count == 5 && scene.items().spawned() == 6, "live miss spawns use pool and shared ring");
}
void tile_contracts() {
    std::vector<std::uint8_t> bytes(54+128,0);
    bytes[0]='M';bytes[1]='P';bytes[2]='T';bytes[3]='N';
    bytes[54]=0x80;bytes[54+32]=0x40;bytes[54+64]=0x80;bytes[54+96]=0x40;
    th04::portable::stage::TileImages tile(bytes);
    require(tile.count()==1 && tile.pixel(0,0,0)==5 && tile.pixel(0,1,0)==10 && tile.pixel(0,8,0)==0,
            "MPN inclusive image count, BRGI planes and left bit order");
    bytes.pop_back();
    bool rejected=false;
    try { th04::portable::stage::TileImages invalid(bytes); } catch(const std::invalid_argument&) { rejected=true; }
    require(rejected,"truncated MPN rejected");
}
void sprite_contracts() {
    std::vector<std::uint8_t> bytes(80+8*2/2,0);
    bytes[0]='B';bytes[1]='F';bytes[2]='N';bytes[3]='T';bytes[4]=26;bytes[5]=0x83;
    bytes[8]=8;bytes[10]=2;
    bytes[32+3]=0x10;bytes[32+4]=0x20;bytes[32+5]=0x30;
    bytes[80]=0x10;bytes[84]=0x21;
    th04::portable::sprite::Sheet sheet(bytes);
    require(sheet.palette()[3]==0x20 && sheet.palette()[4]==0x30 && sheet.palette()[5]==0x10,
            "BFNT BRG to RGB");
    require(sheet.pixel(0,0,0)==1 && sheet.pixel(0,1,0)==0 && sheet.pixel(0,0,1)==2,
            "BFNT high nibble and top-down rows");
    bytes.pop_back();
    bool rejected=false;
    try { th04::portable::sprite::Sheet invalid(bytes); } catch(const std::invalid_argument&) { rejected=true; }
    require(rejected,"truncated BFNT rejected");
}
} // namespace
int main(int argc, char** argv) {
    static_assert(sizeof(void*)==8,"native MAIN requires x64");
    if (argc == 4 && std::string(argv[1]) == "--tile-pixels") {
        std::ifstream file(argv[2],std::ios::binary);
        if (!file) throw std::runtime_error("cannot read tile fixture");
        const std::vector<std::uint8_t> bytes(std::istreambuf_iterator<char>(file),{});
        th04::portable::stage::TileImages tiles(bytes);
        std::ofstream output(argv[3],std::ios::binary);
        if (!output) throw std::runtime_error("cannot write tile pixels");
        for (unsigned image=0; image<tiles.count(); ++image) for (unsigned y=0; y<16; ++y) {
            for (unsigned x=0; x<16; ++x) output.put(static_cast<char>(tiles.pixel(image,x,y)));
        }
        if (!output) throw std::runtime_error("tile pixel write failed");
        return 0;
    }
    if (argc == 4 && std::string(argv[1]) == "--background-trace") {
        const auto read = [](const char* path) {
            std::ifstream file(path,std::ios::binary);
            if (!file) throw std::runtime_error("cannot read background fixture");
            return std::vector<std::uint8_t>(std::istreambuf_iterator<char>(file),{});
        };
        th04::portable::stage::Background bg(read(argv[2]),read(argv[3]));
        unsigned stopped_frames = 0;
        for (unsigned frame=0; frame<20000; ++frame) {
            std::uint32_t hash = 2166136261u;
            for (const auto& row : bg.ring()) for (const auto tile : row) {
                hash = (hash ^ (tile & 255u))*16777619u;
                hash = (hash ^ (tile >> 8))*16777619u;
            }
            std::cout << frame << ' ' << bg.scroll_line() << ' ' << bg.display_line()
                      << ' ' << bg.speed() << ' ' << bg.section_cursor() << ' '
                      << bg.row_in_section() << ' ' << hash << ' ' << bg.last_delta() << '\n';
            if (bg.stopped() && ++stopped_frames == 64) return 0;
            bg.update();
        }
        throw std::runtime_error("background failed to reach STD terminator");
    }
    if (argc == 2 && std::string(argv[1]) == "--movement-vectors") {
        for (unsigned high = 0; high < 16; ++high) {
            for (unsigned low = 0; low < 16; ++low) {
                const auto input = static_cast<std::uint16_t>((high << 8) | low);
                p::Movement player;
                player.update(input, false);
                std::cout << input << ' ' << player.position().velocity.x << ' '
                          << player.position().velocity.y << '\n';
            }
        }
        return 0;
    }
    motion_contracts();pool_contracts();main_contracts();sprite_contracts();tile_contracts();
    std::cout << "TH04 live MAIN contracts: PASS motion=Q12.4 player=HELD_KEYS items=32 sprites=BFNT pointer_bits=64\n";
}

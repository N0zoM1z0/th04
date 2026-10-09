#include "main_state.hpp"
#include "motion_tables.hpp"
#include "sprite_sheet.hpp"
#include "stage_background.hpp"
#include "host_score.hpp"
#include <filesystem>
#include <chrono>
#include <sstream>
#include <fstream>
#include <iterator>
#include <iostream>
#include <iomanip>
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
void fresh_main_contracts(bool print) {
    for(unsigned character=0;character<2;++character)for(unsigned shot=0;shot<2;++shot)
    for(unsigned extra=0;extra<2;++extra)for(unsigned marker:{0u,19u,255u}) {
        a::State application;application.start_normal(a::Playchar(character),a::ShotType(shot));
        a::RunStatistics outgoing;
        for(unsigned d=0;d<8;++d)outgoing.score_digits[d]=std::uint8_t((marker+d)%10);
        application.finish_main(outgoing,a::EndSequence::score);application.finish_maine();
        if(extra)application.start_extra(a::Playchar(character),a::ShotType(shot));
        else application.start_normal(a::Playchar(character),a::ShotType(shot));
        application.add_stage_graze(std::uint16_t(marker*257));
        application.publish_player_statistics(std::uint8_t(marker),std::uint8_t(marker));
        if(extra)application.prepare_main_extra();else application.prepare_main_score();
        const auto generation=application.generation();g::State main(application);
        const auto& resident=application.resident();
        require(resident.graze==0 && resident.miss_count==0 && resident.bombs_used==0 &&
            resident.end_sequence==a::EndSequence::in_game && resident.score_digits==outgoing.score_digits &&
            main.scoreboard().digits==std::array<std::uint8_t,8>{} && main.score().score_delta==0 &&
            application.generation()==generation,"fresh MAIN failed its own gameplay-session resets");
        if(print) {
            std::cout<<resident.graze<<' '<<+resident.miss_count<<' '<<+resident.bombs_used<<' '<<+std::uint8_t(resident.end_sequence)<<' '<<+std::uint8_t(resident.playchar);
            for(auto d:main.scoreboard().digits)std::cout<<' '<<+d;
            for(auto d:resident.score_digits)std::cout<<' '<<+d;
            std::cout<<'\n';
        }
    }
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
    require(scene.score().score_delta==0 && scene.scoreboard().digits[1]==1 &&
            scene.awarded_score_units()==1,"item award drained at the end of its actual frame");
    a::State score_application;score_application.start_normal(a::Playchar::reimu,a::ShotType::a);
    g::State scored(score_application);std::uint32_t awarded=0;unsigned sounds=0;
    for(unsigned frame=0;frame<900;++frame) {
        if(frame<120 && frame%2==0) for(unsigned i=0;i<32;++i)
            require(scored.add_item({192*16,323*16},i::Type::point),"point fixture pool capacity");
        scored.update(0,false);
        for(const auto& e:scored.item_events().events) if(e.collected) awarded+=e.collection.awarded_points;
        require(scored.awarded_score_units()==awarded,"live awards conserved across decimal drain");
        for(const auto& e:scored.score_events()) if(e.kind==th04::portable::score::Kind::sound) {
            ++sounds;require(e.value==7 && scored.bullets().snapshot().clear_time==20,
                             "extend propagates its sound request and same-frame clear timer");
        }
    }
    require(scored.score().score_delta==0 && scored.score().remaining_lives==5 && sounds==2,
            "two actual score extends drain once and publish the live resources");
    const auto drops = scene.add_miss_items();
    require(drops.count == 5 && scene.items().spawned() == 6, "live miss spawns use pool and shared ring");
}
std::string suspended_fingerprint(const g::State& scene,const a::State& app) {
    std::ostringstream out;
    const auto& life=scene.life();const auto& player=scene.player().position();
    out<<scene.frames()<<' '<<scene.run_statistics().std_frames<<' '<<scene.random_cursor()<<' '
       <<app.process_random_state()<<' '<<+life.invincibility<<' '<<+life.respawn_time<<' '
       <<player.current.x<<' '<<player.current.y<<' '<<player.velocity.x<<' '<<player.velocity.y<<' '
       <<+scene.shots().snapshot().time<<' '<<scene.items().spawned()<<' '
       <<+scene.bullets().snapshot().clear_time;
    for(const auto& draw:scene.player_draws())out<<' '<<int(draw.kind)<<' '<<draw.left<<' '<<draw.top<<' '<<draw.pattern;
    return out.str();
}
void lifecycle_join_contracts(const std::filesystem::path& directory,bool report) {
    namespace fs=std::filesystem;namespace sf=th04::portable::score_file;
    namespace go=th04::portable::gameover;
    // These are explicit player checkpoints. They exercise the real MAIN
    // suffix and blocking scene, not a claim that a natural route reached it.
    for(unsigned character=0;character<2;++character) {
        a::State app;auto options=app.resident().config;options.lives=2;
        app.apply_options(options);app.start_normal(a::Playchar(character),a::ShotType::a);
        p::LifeState checkpoint;checkpoint.invincibility=0;checkpoint.hit=1;
        g::State scene(app,g::Mode::ordinary,checkpoint);
        scene.add_item({192*16,323*16},i::Type::power);
        scene.update(0,false);
        require(scene.life().miss_time==39 && scene.life().respawn_time==71,
                "ordinary hit arms and advances the real miss prefix");
        // An item still moves during a miss, but cannot be collected.
        require(scene.score().items_collected==0,"miss animation blocks item pickup in live MAIN");
        for(unsigned frame=1;frame<40;++frame) {
            scene.update(0,false);
            if(scene.life().miss_time==1)require(scene.player_draws().empty(),"death frame1 must remain blank in the cached frontend requests");
            if(scene.life().miss_time>=2 && scene.life().miss_time<=32) {
                require(!scene.player_draws().empty() && scene.player_draws().size()<=8,"live death lost its clipped explosion rings");
                // Independent original render controls for this stationary
                // center/radius/angle sequence:8 at32,6 at16,4 at2.
                if(scene.life().miss_time==32)require(scene.player_draws().size()==8,"initial explosion rings differ");
                if(scene.life().miss_time==16)require(scene.player_draws().size()==6,"middle explosion clipping differs");
                if(scene.life().miss_time==2)require(scene.player_draws().size()==4,"late explosion clipping differs");
                for(const auto& draw:scene.player_draws())require(draw.pattern==3,"live death still drew the player/options");
            }
        }
        require(scene.life().miss_time==0 && scene.score().remaining_lives==1 &&
                scene.life().misses==1 && app.resident().miss_count==1 &&
                scene.player().position().current.y==368*16,"miss decrements lives and publishes counters");
        require(scene.bullets().snapshot().clear_time==31,"respawn clear advances once in the bullet suffix");
        for(unsigned frame=0;frame<32;++frame)scene.update(0,false);
        require(scene.player().position().current.y==304*16 && scene.life().respawn_time==0,
                "respawn movement completes across real MAIN frames");
        if(report)std::cout<<"miss character="<<character<<" frames="<<scene.frames()
            <<" misses="<<+app.resident().miss_count<<" lives="<<+scene.score().remaining_lives<<'\n';

        a::State bomb_app;bomb_app.start_normal(a::Playchar(character),a::ShotType::b);
        g::State bomb_scene(bomb_app);bomb_scene.set_player_palette({32,64,96});
        bomb_scene.update(0x800,false);
        require(bomb_scene.frames()==1 && bomb_scene.player_draws().front().kind==p::RenderKind::white,
                "first rendered Bomb frame lost its pre-increment invincible phase");
        require(bomb_scene.life().bomb_frame==1 && bomb_scene.score().remaining_bombs==1 &&
                bomb_app.resident().bombs_used==1,"host X invokes Bomb and publishes its real resource use");
        for(unsigned frame=1;frame<=226;++frame) {
            const auto before=bomb_scene.random_cursor();bomb_scene.update(0x800,false);
            if(frame==48)require(bomb_scene.life().scroll_active==0 && bomb_scene.life().background==2 &&
                bomb_scene.life().palette14==std::array<std::uint8_t,3>{240,176,192} &&
                !bomb_scene.bomb_effect().draws().empty() && bomb_scene.random_cursor()!=before,
                "character Bomb dispatch consumes the shared ring at its render boundary");
            if(frame==176)require(bomb_scene.life().scroll_active==1 && !bomb_scene.life().pull_items &&
                bomb_scene.life().palette14==std::array<std::uint8_t,3>{32,64,96},
                "Bomb restores palette and scrolling at frame176");
        }
        require(!bomb_scene.life().bombing && bomb_scene.life().palette_tone==100 &&
                bomb_scene.life().circle_color==13 && bomb_scene.life().bombs_used==1,
                "held X cannot restart an active Bomb; frame226 restores final state");
        if(report)std::cout<<"bomb character="<<character<<" frames="<<bomb_scene.frames()
            <<" used="<<+bomb_app.resident().bombs_used<<" cursor="<<bomb_scene.random_cursor()<<'\n';
    }
    for(bool fail:{false,true}) {
        a::State app;auto options=app.resident().config;options.lives=1;
        app.apply_options(options);app.start_normal(a::Playchar::reimu,a::ShotType::a);
        p::LifeState checkpoint;checkpoint.invincibility=0;checkpoint.hit=1;
        g::State scene(app,g::Mode::ordinary,checkpoint);
        const auto location=directory/(fail ? "failed" : "continued");
        sf::HostStore store(location);
        if(fail) {std::ofstream blocker(location);blocker<<"not a directory";}
        unsigned calls=0;
        scene.set_continue_save([&](const th04::portable::score::Digits& old) {
            ++calls;
            require(old[0]==0 && scene.score().remaining_lives==1 && scene.life().misses==1,
                    "Continue persists old score before resetting resources");
            store.save_continue(0,options.rank,app.resident().stage,options.turbo,old,
                                [&]{return app.next_process_random();});
        });
        for(unsigned frame=0;frame<40;++frame)scene.update(0,false);
        require(scene.game_over() && scene.frames()==39,"last life suspends inside player_update before its suffix");
        const auto frozen=suspended_fingerprint(scene,app);
        for(unsigned tick=0;tick<1000 && scene.game_over()->phase()!=go::Phase::press;++tick) {
            scene.update(0x20,false);
            require(frozen==suspended_fingerprint(scene,app),"Game Over held-key clocks cannot advance MAIN state");
            if(scene.game_over()->phase()==go::Phase::release)break;
        }
        require(scene.game_over()->phase()==go::Phase::release,"held acknowledgement waits for release");
        scene.update(0,false);scene.update(0,false);
        require(scene.game_over()->phase()==go::Phase::press,"two-sample release reaches fresh press");
        scene.update(0x20,false);scene.update(0,false);scene.update(0,false);
        require(scene.game_over()->phase()==go::Phase::menu,"fresh acknowledgement enters Continue menu");
        bool rejected=false;
        try {scene.update(0x1000,false);}catch(const fs::filesystem_error&) {rejected=true;}
        require(calls==1,"Continue consumer called exactly once");
        if(fail) {
            require(rejected && scene.frames()==39 && scene.scoreboard().digits[0]==0 &&
                    store.commits()==0 && !fs::exists(location/"GENSOU.SCR"),
                    "failed host write rejects Continue before resource and frame reset");
        } else {
            require(!rejected && store.commits()==1 && scene.scoreboard().digits[0]==1,
                    "missing score file is committed at the original writer close");
            // Save is the sole process-RNG operation while MAIN is blocked.
            const auto saved_rng=app.process_random_state();const auto saved_ring=scene.random_cursor();
            while(scene.game_over()) {
                scene.update(0,false);
                require(app.process_random_state()==saved_rng && scene.random_cursor()==saved_ring,
                        "Continue fade/resumed suffix does not repeat miss-drop RNG");
            }
            if(report)std::cout<<"resume "<<suspended_fingerprint(scene,app)<<'\n';
            require(scene.frames()==40 && scene.player().position().current.y==368*16 &&
                    scene.life().respawn_time==32 && scene.life().invincibility==153 &&
                    scene.shots().snapshot().time==0,"Continue resumes exactly the interrupted frame suffix");
            scene.update(0,false);
            require(scene.frames()==41 && scene.player().position().current.y==366*16 &&
                    scene.life().respawn_time==31,"the next frame performs the next player prefix once");
            sf::HostStore restarted(location);
            require(restarted.file().bytes()==store.file().bytes(),"fresh host instance reads the actual committed file");
        }
        if(report)std::cout<<"continue failed="<<fail<<" calls="<<calls<<" commits="<<store.commits()
            <<" frames="<<scene.frames()<<" credit_digit="<<+scene.scoreboard().digits[0]<<'\n';
    }
    // The host wrapper uses MAIN's single-draw cipher, and changes only the
    // selected section after a complete file already exists.
    const auto ranked=directory/"ranked";sf::HostStore store(ranked);
    unsigned draws=0;auto next=[&]() {++draws;return std::uint16_t(draws*257);};
    th04::portable::score::Digits digits{};digits[7]=9;
    for(unsigned character=0;character<2;++character)for(unsigned rank=0;rank<5;++rank) {
        const auto previous=store.file().bytes();const auto before=draws;
        require(store.save_continue(character,rank,rank==4 ? 6 : 2,true,digits,next)==0,
                "ranked Continue enters the selected section");
        require(draws-before==(previous.empty() ? 11u : 1u),"MAIN recreate/save retains one RNG word per key");
        sf::Section section{};const auto section_index=character*5+rank;
        std::copy_n(store.file().bytes().begin()+section_index*sf::section_size,sf::section_size,section.begin());
        require(sf::decode(section)==0,"fresh host Continue section checksum");
        const std::array<std::uint8_t,8> name{0xac,0xb8,0xb7,0xbd,0xb2,0xb7,0xbe,0xae};
        require(std::equal(name.begin(),name.end(),section.begin()+sf::names_offset) &&
                section[sf::digits_offset+7]==0xa9,"saved Continue name and pre-reset digits survive decoding");
        if(!previous.empty())for(unsigned at=0;at<previous.size();++at)
            if(at/sf::section_size!=section_index)require(previous[at]==store.file().bytes()[at],
                "Continue does not re-key an unrelated section");
    }
    require(store.commits()==11,"ten ranked saves plus one recreate close");
    const auto before=store.file().bytes();const auto before_draws=draws;
    require(store.save_continue(0,1,0,false,digits,next)==sf::no_entry &&
            store.file().bytes()==before && store.commits()==11 && draws==before_draws,
            "non-Turbo loads without saving an existing complete score file");
    if(report)std::cout<<"sections=10 commits="<<store.commits()<<" rng_draws="<<draws<<" non_turbo=read_only\n";

    p::LifeState final_checkpoint;final_checkpoint.miss_time=1;final_checkpoint.respawn_time=33;
    // One-credit Final Stage checkpoint bypasses Game Over entirely.
    a::State bad_app;auto options=bad_app.resident().config;options.lives=1;
    bad_app.apply_options(options);bad_app.start_normal(a::Playchar::marisa,a::ShotType::b);
    for(unsigned stage=0;stage<5;++stage)bad_app.advance_main_stage();
    bad_app.publish_main_resource_stage(5);
    g::State bad(bad_app,g::Mode::ordinary,final_checkpoint);bad.update(0,false);
    require(bad.bad_ending_requested() && bad.frames()==0 && bad.game_over()->ticks()==0,
            "Final Stage last life requests Bad Ending without menu or frame tail");
    a::State quit_app;quit_app.apply_options(options);quit_app.start_normal(a::Playchar::reimu,a::ShotType::a);
    g::State quit(quit_app,g::Mode::ordinary,final_checkpoint);quit.update(0,false);
    while(quit.game_over()->phase()!=go::Phase::press)quit.update(0,false);
    quit.update(0x20,false);quit.update(0,false);quit.update(0,false);quit.update(0x2000,false);
    for(unsigned tick=0;tick<1000 && !quit.score_registration_requested();++tick)quit.update(0,false);
    require(quit.score_registration_requested() && quit.frames()==0 &&
            quit_app.resident().end_sequence==a::EndSequence::score,"Quit publishes score route after blackout without MAIN suffix");
    if(report)std::cout<<"quit score_route=1 final_stage_bad=1 main_frames=0\n";
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
template<class Bytes>
std::string bytes_hex(const Bytes& bytes) {
    std::ostringstream out;out<<std::hex<<std::setfill('0');
    for(auto byte:bytes)out<<std::setw(2)<<unsigned(byte);
    return out.str().empty() ? "-" : out.str();
}
void main_hud_vectors(const std::filesystem::path& fixtures,const std::filesystem::path& directory) {
    namespace sf=th04::portable::score_file;
    require(!std::filesystem::exists(directory),"MAIN HUD outputs must be fresh");
    std::filesystem::create_directories(directory);
    std::ifstream input(fixtures);require(bool(input),"MAIN HUD vectors missing");
    unsigned character,rank,seed,present,index=0;std::string text;
    while(input>>character>>rank>>seed>>present>>text) {
        require(character<2 && rank<5 && seed<=4096 && present<=1,"invalid MAIN HUD context");
        sf::Bytes data;
        if(text!="-") {
            require(text.size()%2==0,"invalid score fixture hex");
            for(unsigned at=0;at<text.size();at+=2)data.push_back(std::uint8_t(std::stoul(text.substr(at,2),nullptr,16)));
        }
        const auto save=directory/std::to_string(index++);std::filesystem::create_directory(save);
        if(present) {
            std::ofstream file(save/"GENSOU.SCR",std::ios::binary);
            file.write(reinterpret_cast<const char*>(data.data()),std::streamsize(data.size()));require(bool(file),"cannot seed native score fixture");
        }
        a::State app;auto options=app.resident().config;options.rank=std::uint8_t(rank==4 ? 1 : rank);
        app.apply_options(options);for(unsigned i=0;i<seed;++i)app.advance_op_menu_frame();
        if(rank==4)app.start_extra(a::Playchar(character),a::ShotType::a);
        else app.start_normal(a::Playchar(character),a::ShotType::a);
        sf::HostStore store(save);g::State main(app,g::Mode::ordinary,{},&store);
        sf::HostStore reopened(save);
        require(store.file().bytes()==reopened.file().bytes(),"MAIN repair did not physically close before return");
        sf::Bytes angles;for(const auto& spark:main.sparks().snapshot().entities) {
            angles.push_back(std::uint8_t(spark.angle));angles.push_back(std::uint8_t(spark.angle>>8));
        }
        std::cout<<app.process_random_state()<<' '<<main.random_cursor()<<' '<<+main.drop_cycle()<<' '
            <<main.hud_hp_previous()<<' '<<bytes_hex(main.scoreboard().digits)<<' '<<bytes_hex(main.scoreboard().hiscore)
            <<' '<<bytes_hex(main.random_ring_bytes())<<' '<<bytes_hex(angles)<<' '<<bytes_hex(main.hud_text_plane().bytes())
            <<' '<<bytes_hex(reopened.file().bytes())<<' '<<store.commits()<<'\n';
    }
    require(input.eof() && index>0,"truncated MAIN HUD vector");
}
void main_hud_contracts(const std::filesystem::path& directory) {
    namespace sf=th04::portable::score_file;
    namespace mb=th04::portable::midboss;
    namespace hud=th04::portable::hud;
    const auto save=directory/"main-hud";std::filesystem::create_directory(save);
    sf::Bytes file;
    for(unsigned section=0;section<10;++section) {
        sf::Section row{};sf::initialize_rows(row);
        for(unsigned d=0;d<8;++d)row[sf::digits_offset+d]=std::uint8_t(0xa0+(section+d)%10);
        sf::encode_main(row,[section]{return std::uint16_t(1234+section);});
        file.insert(file.end(),row.begin(),row.end());
    }
    {std::ofstream out(save/"GENSOU.SCR",std::ios::binary);out.write(reinterpret_cast<const char*>(file.data()),file.size());require(bool(out),"cannot seed MAIN HUD contract");}
    for(unsigned character=0;character<2;++character)for(unsigned rank=0;rank<5;++rank) {
        a::State app;auto options=app.resident().config;options.rank=std::uint8_t(rank==4 ? 1 : rank);app.apply_options(options);
        if(rank==4)app.start_extra(a::Playchar(character),a::ShotType::a);else app.start_normal(a::Playchar(character),a::ShotType::a);
        sf::HostStore store(save);g::State main(app,g::Mode::ordinary,{},&store);
        for(unsigned d=0;d<8;++d)require(main.scoreboard().hiscore[d]==(character*5+rank+d)%10,"MAIN read wrong physical high-score section");
        require(main.scoreboard().digits==th04::portable::score::Digits{} && store.commits()==0 && store.file().bytes()==file,
                "valid MAIN score load must be read-only and preserve local zero score");
        const auto initial=main.hud_text_plane().bytes();main.update(0x800,false);
        const auto bomb=main.hud_text_plane().bytes();const auto at=(11*80+64)*2;
        require(initial[at]==0x57 && initial[at+1]==0x53 && bomb[at]==0x56 && bomb[at+1]==2,
                "ordinary Bomb did not erase its second HUD icon at the resource event");
    }
    // The actor's stale replay metadata must not override MAIN's shared HP
    // previous; the following boss uses the same animator, and visual clear
    // preserves it. Isolated controls still retain their own explicit context.
    mb::Snapshot actor;actor.active=true;actor.hp_bar=127;
    mb::System midboss(actor);mb::Context context;context.hp_previous=nullptr;
    std::int16_t previous=63;context.hp_previous=&previous;
    th04::portable::bullet::System bullets;th04::portable::randring::SharedRandomRing ring;
    th04::portable::rng::Lcg32 random;ring.fill(random);
    midboss.update(context,bullets,ring);
    require(previous==64 && midboss.snapshot().hp_bar==64,"midboss did not use shared MAIN HP previous exactly once");
    th04::portable::registration::TextPlane plane;hud::apply(plane,hud::hp_update(previous,100,100));
    require(previous==65,"boss repeated or reset the midboss HP animation");
    hud::Values values;hud::apply(plane,hud::initialize(values));
    require(previous==65,"stage HUD clear reset shared HP animation");
    // Observe every collected slot before the next pickup mutates its values.
    i::Pool pool;i::ScoreState score;
    pool.add({192*16,323*16},i::Type::dream);pool.add({192*16,323*16},i::Type::dream);
    std::vector<std::uint16_t> seen;
    pool.update(score,{192*16,320*16},false,0,[&](const auto& effects,const auto& current) {
        require(effects.hud_dream_changed,"dream pickup omitted its HUD boundary");seen.push_back(current.dream_score);
    });
    require(seen==std::vector<std::uint16_t>{100,200},"mixed pickup consumer lost per-slot dream state");
}
} // namespace
int main(int argc, char** argv) {
    if(argc==4 && std::string(argv[1])=="--main-hud-join") {
        main_hud_vectors(argv[2],argv[3]);return 0;
    }
    if(argc==2 && std::string(argv[1])=="--fresh-main-vectors") {fresh_main_contracts(true);return 0;}
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
    if(argc==3 && std::string(argv[1])=="--lifecycle-join") {
        const std::filesystem::path directory(argv[2]);
        if(std::filesystem::exists(directory))throw std::runtime_error("lifecycle output must be fresh");
        std::filesystem::create_directories(directory);lifecycle_join_contracts(directory,true);return 0;
    }
    const auto temporary=std::filesystem::temp_directory_path()/
        ("th04-lifecycle-"+std::to_string(std::chrono::steady_clock::now().time_since_epoch().count()));
    if(!std::filesystem::create_directory(temporary))throw std::runtime_error("cannot reserve lifecycle contract directory");
    struct Cleanup {std::filesystem::path path;~Cleanup(){std::error_code error;std::filesystem::remove_all(path,error);}} cleanup{temporary};
    lifecycle_join_contracts(temporary,false);
    main_hud_contracts(temporary);
    fresh_main_contracts(false);motion_contracts();pool_contracts();main_contracts();sprite_contracts();tile_contracts();
    std::cout << "TH04 live MAIN contracts: PASS motion=Q12.4 player=HELD_KEYS items=32 sprites=BFNT pointer_bits=64\n";
}

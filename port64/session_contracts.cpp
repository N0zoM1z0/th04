#include "stage_session.hpp"
#include "main_state.hpp"
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <iterator>
using namespace th04::portable;
namespace {
template<class T> void out(T v) { std::cout<<+v<<' '; }
void point(motion::Point p) { out(p.x);out(p.y); }
void reset(std::uint32_t seed,unsigned marker,std::uint32_t pending,unsigned clear,unsigned offset,bool print,unsigned repeats=1) {
    player::Movement p;p.update(player::left,false);const auto latch=p.previous_input();
    shot::Snapshot sh;sh.time=marker;sh.reimu_cycle=marker;sh.spark_cycle=marker;
    sh.laser.time=marker*257;sh.laser.style=static_cast<shot::LaserStyle>(marker%5);
    for(auto& e:sh.entities) { e.flag=1;e.age=marker;e.position.current={123,-456}; }
    shot::System shots(sh);enemy::Snapshot es;
    for(auto& e:es.entities) { e.flag=1;e.age=marker;e.position.current={123,-456}; }
    enemy::System enemies(es);bullet::Snapshot bs;bs.clear_time=clear;bs.zap_frame=marker;bs.graze=65535;
    for(auto& e:bs.entities) { e.flag=1;e.age=marker;e.position.current={123,-456}; }
    bullet::System bullets(bs);spark::Snapshot ss;ss.ring_offset=offset;
    for(auto& e:ss.entities) { e.flag=1;e.age=marker;e.center.current={123,-456};e.angle=65535; }
    spark::System sparks(ss);gather::Snapshot gs;
    for(auto& e:gs.entities) { e.flag=1;e.center.current={123,-456}; }
    gs.scratch.center={123,-456};gs.scratch.velocity={123,-456};
    gather::System gathers(gs);circle::Snapshot cs;
    for(auto& e:cs.entities) { e.flag=1;e.center={123,-456}; }
    circle::System circles(cs);item::Pool items;items.add({123,456},item::Type::point);
    item::ScoreState awards;awards.power=marker;awards.score_delta=pending;
    awards.stage_point_items_collected=marker;awards.dream_items_collected=marker;awards.dream_score=65535;
    score::Snapshot score;score.delta=pending;score.performance=marker;
    score.digits.fill(marker);score.hiscore.fill(static_cast<std::uint8_t>(marker+1));
    randring::SharedRandomRing random;item::EnemyDropSequence drops(255);rng::Lcg32 process(seed);
    for(unsigned stage=0;stage<repeats;++stage) session::initialize_actors({p,shots,enemies,bullets,sparks,gathers,circles,items,awards,score,random,drops},[&]{return process.next_byte();});
    if(p.previous_input()!=latch || awards.score_delta!=pending || awards.power!=marker)
        throw std::runtime_error("stage reset changed process-wide input/score/power");
    if(items.spawned()!=1)
        throw std::runtime_error("stage reset erased the run's cumulative item count");
    if(!print) return;
    point(p.position().current);point(p.position().previous);point(p.position().velocity);
    const auto& s=shots.snapshot();out(s.time);out(s.laser.time);out(unsigned(s.laser.style));out(s.reimu_cycle);out(s.spark_cycle);
    out(bullets.snapshot().clear_time);out(bullets.snapshot().graze);out(bullets.snapshot().zap_frame);out(circles.snapshot().color);
    const auto& g=gathers.snapshot().scratch;point(g.center);point(g.velocity);out(g.radius);out(g.ring_points);out(g.color);out(g.angle_delta);
    out(sparks.snapshot().ring_offset);out(process.state());out(drops.cycle());out(awards.power);
    out(awards.stage_point_items_collected);out(awards.dream_items_collected);out(awards.dream_score);out(awards.score_delta);out(score.delta);out(score.performance);
    for(const auto* digits:{&score.digits,&score.hiscore,&score.hud}) for(auto digit:*digits) out(digit);
    for(const auto& e:sparks.snapshot().entities) out(e.angle);
    for(unsigned i=0;i<256;++i) out(random.next16());
    unsigned alive=0;
    for(const auto& e:s.entities) alive+=e.flag!=0 || e.position.current.x || e.position.current.y;
    for(const auto& e:enemies.snapshot().entities) alive+=e.flag!=0 || e.position.current.x || e.position.current.y;
    for(const auto& e:bullets.snapshot().entities) alive+=e.flag!=0 || e.position.current.x || e.position.current.y;
    for(const auto& e:sparks.snapshot().entities) alive+=e.flag!=0 || e.center.current.x || e.center.current.y;
    for(const auto& e:gathers.snapshot().entities) alive+=e.flag!=0 || e.center.current.x || e.center.current.y;
    for(const auto& e:circles.snapshot().entities) alive+=e.flag!=0 || e.center.x || e.center.y;
    for(const auto& e:items.entities()) alive+=e.flag!=item::Flag::free || e.position.current.x || e.position.current.y;
    std::cout<<alive<<'\n';
}
void check_midboss(unsigned marker) {
    midboss::Snapshot s;s.position.current=s.position.previous={123,-456};s.position.velocity={17,-19};
    s.start_frame=99;s.hp=17;s.sprite=19;s.phase=marker;s.phase_frame=motion::wrap(marker*257);
    s.damaged=marker;s.unused_angle=marker^55;s.active=true;
    s=session::prepare_stage2_midboss(s);
    point(s.position.current);point(s.position.previous);point(s.position.velocity);
    out(s.start_frame);out(s.hp);out(s.sprite);out(s.phase);out(s.phase_frame);out(s.damaged);out(s.unused_angle);std::cout<<s.active<<'\n';
}
stage::Program::Bytes read(const char* name) {
    std::ifstream file(name,std::ios::binary);if(!file) throw std::runtime_error("cannot read stage resource");
    return {std::istreambuf_iterator<char>(file),{}};
}
void replay(char** paths) {
    const auto first=read(paths[0]),map0=read(paths[1]),second=read(paths[2]),map1=read(paths[3]);
    for(unsigned character=0;character<2;++character) for(unsigned rank:{1u,3u}) {
        application::State application;auto options=application.resident().config;options.rank=rank;
        application.apply_options(options);application.start_normal(static_cast<application::Playchar>(character),application::ShotType::a);
        gameplay::State main(application,gameplay::Mode::actor_control);main.load_stage(first);stage::Background background(map0,first);
        for(unsigned tick=0;tick<20000 && !main.next_stage_requested();++tick) {
            if(main.stage1_dialog_ready(background)) main.start_orange_after_dialog();
            if(main.post_boss_dialog_pending()) main.finish_post_boss_dialog();
            const auto frame=main.frames();main.update(shot::input_shot,false,false,background.last_delta(),&background);
            if(main.frames()!=frame && !main.next_stage_requested()) background.update();
        }
        if(!main.next_stage_requested()) throw std::runtime_error("natural Stage1 did not request Stage2");
        const auto awards=main.score();const auto board=main.scoreboard();const auto generation=application.generation();const auto before=application.process_random_state();
        // Invalid STD must be rejected before any owner or process RNG changes.
        try { main.prepare_next_stage_actors({0});throw std::logic_error("bad STD passed"); }
        catch(const std::invalid_argument&) {}
        if(before!=application.process_random_state() || awards.score_delta!=main.score().score_delta || !main.next_stage_requested()) throw std::runtime_error("invalid stage partially changed owners");
        main.prepare_next_stage_actors(second);rng::Lcg32 expected(before);for(unsigned i=0;i<353;++i) expected.next_byte();
        if(application.generation()!=generation || application.process_random_state()!=expected.state() || main.frames()!=0 || main.random_cursor()!=0) throw std::runtime_error("stage2 replaced MAIN or reseeded/refilled RNG incorrectly");
        if(main.score().power!=awards.power || main.score().power_overflow!=awards.power_overflow || main.score().score_delta!=awards.score_delta || main.scoreboard().digits!=board.digits || main.scoreboard().hiscore!=board.hiscore || main.scoreboard().performance!=board.performance) throw std::runtime_error("stage2 reset persistent gameplay awards");
        if(main.score().stage_point_items_collected || main.score().dream_items_collected || main.score().dream_score || main.bullets().snapshot().graze || main.orange_active()) throw std::runtime_error("stage2 retained old stage owners");
        if(main.player().position().current.x!=3072 || main.player().position().current.y!=5120 || main.midboss_state().hp!=750 || main.midboss_state().start_frame!=2600 || main.midboss_state().position.current.y!=-512) throw std::runtime_error("stage2 position/midboss seed differs");
        stage::Background next_background(map1,second);
        bool activated=false,completed=false;unsigned draws=0,gather_requests=0,bomb_requests=0;
        for(unsigned tick=0;tick<20000 && !main.stage2_dialog_ready(next_background);++tick) {
            const auto frame=main.frames();main.update(shot::input_shot,false,false,next_background.last_delta(),&next_background);
            if(frame==2600) {
                if(!main.midboss_state().active || main.midboss_state().phase_frame!=1) throw std::runtime_error("Stage2 midboss activation did not enter actual callback");
                activated=true;
            }
            if(activated && !main.midboss_state().active) completed=true;
            if(main.midboss_state().active) draws+=main.midboss_draws().size();
            for(const auto& event:main.midboss_events()) {
                gather_requests+=event.type==midboss::EventType::gather;
                bomb_requests+=event.type==midboss::EventType::item;
            }
            if(main.frames()!=frame) next_background.update();
        }
        const auto stopped=main.frames();const auto cursor=main.random_cursor();const auto score=main.awarded_score_units();
        for(unsigned i=0;i<3;++i) main.update(shot::input_shot|player::left,false,false,0,&next_background);
        if(!activated || !completed || !draws || !main.stage2_dialog_ready(next_background) || main.frames()!=stopped || main.random_cursor()!=cursor || main.awarded_score_units()!=score || main.midboss_state().active || main.midboss().snapshot().active) throw std::runtime_error("Stage2 midboss or pre-Kurumi dialog frontier differs");
        std::cout<<"Stage2 actors character="<<character<<" rank="<<rank<<" frame="<<stopped<<" power="<<+main.score().power<<" pending="<<main.score().score_delta<<" score="<<score<<" rng="<<application.process_random_state()<<" generation="<<generation<<" midboss_draws="<<draws<<" gather_requests="<<gather_requests<<" bomb_requests="<<bomb_requests<<" boundary=kurumi_dialog_pending\n";
    }
}
}
int main(int argc,char** argv) {
    try {
        if(argc==6 && std::string(argv[1])=="--stage2-actors") replay(argv+2);
        else if(argc==3 && std::string(argv[1])=="--vectors") {
            std::ifstream file(argv[2]);if(!file) throw std::runtime_error("cannot read session vectors");char op;
            while(file>>op) {
                if(op=='R' || op=='Q') { std::uint32_t seed,pending;unsigned marker,clear,offset;file>>seed>>marker>>pending>>clear>>offset;if(!file) throw std::runtime_error("short reset vector");reset(seed,marker,pending,clear,offset,true,op=='Q' ? 2 : 1); }
                else if(op=='M') { unsigned marker;file>>marker;if(!file) throw std::runtime_error("short midboss seed");check_midboss(marker); }
                else throw std::runtime_error("unknown session vector");
            }
        } else {
            reset(318,255,1997011721,20,0x12ff,false);
            std::cout<<"stage_actors=REINITIALIZED pending_score=PRESERVED rng_draws=353 stage2_midboss=2600 pointer_bits=64\n";
        }
        return 0;
    } catch(const std::exception& e) { std::cerr<<e.what()<<'\n';return 1; }
}

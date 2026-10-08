#include "player_lifecycle.hpp"
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>

bool gameover_cli(int argc,char** argv);
bool gameover_render_cli(int argc,char** argv);
void gameover_contracts();
bool bomb_cli(int argc,char** argv);
void bomb_contracts();

namespace p=th04::portable::player;
namespace s=th04::portable::shot;
namespace m=th04::portable::motion;
namespace item=th04::portable::item;
namespace {
void require(bool b,const char* message) {if(!b)throw std::runtime_error(message);}
struct Fixture {
    p::LifeState life;
    item::ScoreState score;
    m::Motion motion;
    std::uint16_t old_input=0,laser_time=0,keys=0,scroll_line=0;
    std::uint8_t shot_time=0,performance=16,minimum=11,credit=2,game_over=1;
    bool shift=false;
};
Fixture parse(std::istream& input) {
    Fixture f;
    const auto n=[&] {int value=0;require(bool(input>>value),"incomplete lifecycle fixture");return value;};
    auto& l=f.life;
    l.invincibility=n();l.hit=n();l.miss_time=n();l.respawn_time=n();
    l.explosion_radius=n();l.explosion_angle=n();l.misses=n();l.bombs_used=n();l.quit=n();
    l.bombing=n();l.bomb_frame=n();l.bombing_disabled=n();l.clear_time=n();
    l.pull_items=n();l.scroll_active=n();l.background=n();l.circle_color=n();
    l.palette_tone=n();l.palette_changed=n();
    for(auto& x:l.palette14)x=n();
    for(auto& x:l.palette_backup)x=n();
    l.options={m::Subpixel(n()),m::Subpixel(n())};
    l.previous_options={m::Subpixel(n()),m::Subpixel(n())};
    f.score.power=n();f.score.power_overflow=n();f.score.dream_items_collected=n();
    f.score.dream_score=n();f.score.remaining_lives=n();f.score.remaining_bombs=n();
    f.performance=n();f.minimum=n();f.credit=n();f.scroll_line=n();
    f.motion.current={m::Subpixel(n()),m::Subpixel(n())};
    f.motion.previous={m::Subpixel(n()),m::Subpixel(n())};
    f.motion.velocity={m::Subpixel(n()),m::Subpixel(n())};
    f.old_input=n();f.shot_time=n();f.laser_time=n();f.keys=n();f.shift=n()!=0;f.game_over=n();
    return f;
}
std::string execute(char op,Fixture& f) {
    p::Movement movement(f.motion,f.old_input);
    s::Snapshot shot;shot.time=f.shot_time;shot.laser.time=f.laser_time;shot.options=f.life.options;
    s::System shots(shot);p::Lifecycle life(f.life);
    std::vector<p::LifeEvent> events;
    p::LifeContext c{f.score,movement,shots,f.performance,f.minimum,f.credit,f.scroll_line,
        [&](const auto& e){events.push_back(e);},[&] {return std::optional<std::uint8_t>(f.game_over);},{}};
    if(op=='U')life.update(f.keys,f.shift,c);
    else if(op=='M')life.miss_update(c);
    else if(op=='B')life.bomb(c);
    else if(op=='R')life.render_bomb(c);
    else throw std::invalid_argument("unknown lifecycle operation");
    f.life=life.state();f.motion=movement.position();f.old_input=movement.previous_input();
    f.shot_time=shots.snapshot().time;f.laser_time=shots.snapshot().laser.time;
    std::ostringstream out;out<<'S';const auto n=[&](auto x){out<<' '<<int(x);};const auto& l=f.life;
    for(auto x:{l.invincibility,l.hit,l.miss_time,l.respawn_time})n(x);
    n(l.explosion_radius);n(l.explosion_angle);n(l.misses);n(l.bombs_used);n(l.quit);
    for(auto x:{l.bombing,l.bomb_frame,l.bombing_disabled,l.clear_time,l.pull_items,
                l.scroll_active,l.background,l.circle_color})n(x);
    n(l.palette_tone);n(l.palette_changed);
    for(auto x:l.palette14)n(x);
    for(auto x:l.palette_backup)n(x);
    for(auto x:{l.options.x,l.options.y,l.previous_options.x,l.previous_options.y})n(x);
    n(f.score.power);n(f.score.power_overflow);n(f.score.dream_items_collected);n(f.score.dream_score);
    n(f.score.remaining_lives);n(f.score.remaining_bombs);n(f.performance);n(f.minimum);n(f.credit);n(f.scroll_line);
    for(auto x:{f.motion.current.x,f.motion.current.y,f.motion.previous.x,f.motion.previous.y,
                f.motion.velocity.x,f.motion.velocity.y})n(x);
    n(f.old_input);n(f.shot_time);n(f.laser_time);
    for(const auto& e:events)out<<'|'<<int(e.kind)<<' '<<e.value;
    return out.str();
}
}
int main(int argc,char** argv) {
    try {
        if(gameover_cli(argc,argv))return 0;
        if(gameover_render_cli(argc,argv))return 0;
        if(bomb_cli(argc,argv))return 0;
        if(argc==3 && std::string(argv[1])=="--vectors") {
            std::ifstream input(argv[2]);require(bool(input),"lifecycle fixture file missing");
            Fixture f;char op;
            while(input>>op) {
                if(op=='N') {unsigned keys,shift;require(bool(input>>keys>>shift),"incomplete retained input");f.keys=keys;f.shift=shift;op='U';}
                else if(op=='T')op='R';
                else f=parse(input);
                std::cout<<execute(op,f)<<'\n';
            }
            return 0;
        }
        gameover_contracts();
        bomb_contracts();
        require(p::input_from_host_actions(0x800)==0x10 &&
            p::input_from_host_actions(0x1000)==0x2000 &&
            p::input_from_host_actions(0x2000)==0x1000,"MAIN host masks differ");
        Fixture f;f.life.invincibility=0;f.life.hit=1;f.score.power=128;
        f.score.remaining_lives=3;f.score.remaining_bombs=2;f.score.dream_items_collected=7;
        f.laser_time=64;f.motion.current=f.motion.previous={3072,5120};
        execute('U',f);
        require(f.life.miss_time==39 && f.life.respawn_time==71 && f.laser_time==33,
            "hit did not arm the deathbomb window");
        for(unsigned i=0;i<7;++i)execute('U',f);
        require(f.life.miss_time==32 && f.score.power==112 && f.score.dream_items_collected==6 &&
                f.life.misses==1,"death threshold did not publish loss once");
        f.keys=0x10;execute('U',f);
        require(!f.life.bombing && f.life.miss_time==31,"late Bomb escaped the death boundary");
        f.keys=0;
        for(unsigned i=0;i<31;++i)execute('U',f);
        require(f.score.remaining_lives==2 && f.score.remaining_bombs==2 && f.life.clear_time==32 &&
                f.motion.current.y==368*16 && f.motion.velocity.y==-32,"respawn resources/position differ");
        for(unsigned i=0;i<32;++i)execute('U',f);
        require(!f.life.respawn_time && f.motion.current.y==304*16,"72-frame motion did not finish");
        f=Fixture{};f.life.invincibility=0;f.life.hit=1;f.score.remaining_bombs=1;f.keys=0x10;
        execute('U',f);
        require(f.life.bombing && !f.life.miss_time && !f.life.respawn_time &&
                f.life.invincibility==255 && f.life.bombs_used==1,"same-refresh deathbomb did not cancel miss");
        for(unsigned i=0;i<227;++i)execute('R',f);
        require(!f.life.bombing && f.life.bomb_frame==227 && f.life.palette_tone==100 &&
                f.life.scroll_active && !f.life.pull_items,"Bomb cleanup did not complete");
        std::cout<<"TH04 player lifecycle: PASS deathbomb=8 miss=32 respawn=72 bomb=227 muted=1\n";
        return 0;
    } catch(const std::exception& e) {std::cerr<<e.what()<<'\n';return 1;}
}

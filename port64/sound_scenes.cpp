#include "sound_scenes.hpp"
#include <stdexcept>
namespace th04::portable::sound {
namespace {
std::string name(const score_file::Bytes& data){return std::string(data.begin(),data.end());}
}
void Timeline::emit(SceneEvent event) const {if(observer_)observer_(event);}
void Timeline::enter(application::Program p,std::uint32_t generation,const menu::Options& options) {
    if(p==application::Program::exited)throw std::invalid_argument("sound cannot enter exited process");
    leave();program_=p;generation_=generation;
    runtime_=std::make_shared<Runtime>(reader_,[this,p,generation](const Action& a){
        emit({SceneKind::action,p,generation,a});
    },Sink{},[this,p,generation](const auto& values){if(samples_)samples_(p,generation,values);});
    emit({SceneKind::enter,p,generation});configure(options);
    // TH04 MAINE determines modes but does not call snd_load(SE). Its newly
    // initialized beeper has no effects; do not borrow MAIN's EFS buffers.
    if(p!=application::Program::maine)handle({ActionKind::load,0xb00,"miko"});
}
void Timeline::leave() {
    if(runtime_)emit({SceneKind::leave,program_,generation_});
    runtime_.reset();program_=application::Program::exited;
}
void Timeline::configure(const menu::Options& options) {
    if(!runtime_)throw std::logic_error("sound configure requires process");
    SceneEvent e{SceneKind::configure,program_,generation_};e.options=options;emit(e);
    runtime_->configure(options.bgm_mode,options.se_mode);
}
void Timeline::op_title(bool demo) {
    if(program_!=application::Program::op)throw std::logic_error("title sound requires OP");
    if(!demo){handle({ActionKind::command,0x100});handle({ActionKind::load,0x600,"op"});handle({ActionKind::command,0});}
}
void Timeline::op_restart(const menu::Options& options) {
    if(program_!=application::Program::op)throw std::logic_error("option sound requires OP");
    handle({ActionKind::command,0x100});configure(options);
    handle({ActionKind::load,0x600,"op"});handle({ActionKind::command,0});
}
void Timeline::handle(const Action& a) {
    if(!runtime_)throw std::logic_error("sound request requires process");
    runtime_->handle(a);
}
void Timeline::measure(int goal,int fallback) {
    SceneEvent e{SceneKind::measure,program_,generation_};e.goal=std::uint16_t(goal);e.fallback=std::uint16_t(fallback);emit(e);
    // The current backend is absent. Consumers retain their original off-BGM
    // fallback; no synthetic measure reply is returned to them.
}
void Timeline::cutscene(const th04::portable::cutscene::Event& e) {
    using K=th04::portable::cutscene::Kind;
    switch(e.kind) {
    case K::bgm_control:handle({ActionKind::command,std::uint16_t(e.a)});break;
    case K::bgm_load:handle({ActionKind::load,std::uint16_t(e.a),e.name});break;
    case K::se_begin:handle({ActionKind::reset});break;
    case K::se:handle({ActionKind::play,std::uint16_t(e.a)});break;
    case K::se_end:handle({ActionKind::immediate_update});break;
    case K::measure:measure(e.a,e.b);break;
    default:break;
    }
}
void Timeline::staff(const th04::portable::staff::Event& e) {
    using K=th04::portable::staff::Kind;
    if(e.kind==K::bgm_control)handle({ActionKind::command,std::uint16_t(e.a)});
    else if(e.kind==K::bgm_load)handle({ActionKind::load,std::uint16_t(e.a),e.name});
    else if(e.kind==K::measure)measure(e.a,e.b);
}
void Timeline::registration(const th04::portable::registration::Event& e) {
    using K=th04::portable::registration::Kind;
    if(e.kind==K::sound)handle({ActionKind::command,std::uint16_t(e.a)});
    else if(e.kind==K::song)handle({ActionKind::load,std::uint16_t(e.a),e.text});
}
void Timeline::ranking(const op_ranking::Event& e) {
    if(e.kind==op_ranking::Kind::sound)handle({ActionKind::command,std::uint16_t(e.a)});
    else if(e.kind==op_ranking::Kind::song)handle({ActionKind::load,std::uint16_t(e.a),name(e.data)});
}
void Timeline::music(const op_music::Event& e) {
    if(e.kind==op_music::Kind::sound)handle({ActionKind::command,std::uint16_t(e.a)});
    else if(e.kind==op_music::Kind::song)handle({ActionKind::load,std::uint16_t(e.a),name(e.data)});
}
}

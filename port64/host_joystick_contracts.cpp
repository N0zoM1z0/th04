// Complete injected APIs only: this executable never opens host devices.
#include "host_joystick_api.hpp"
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>
using namespace th04::portable;
namespace j=host_joystick;
namespace {
void require(bool value,const char* message){if(!value)throw std::runtime_error(message);}
struct Script final:j::Device {
    j::Sample sample{17,0xff};unsigned reads=0;
    j::Sample read() override {++reads;return sample;}
};
void composition() {
    auto device=std::make_unique<Script>();auto* raw=device.get();j::Joystick joystick(std::move(device));
    raw->sample.pins=0xdf;joystick.update(true);
    require(!joystick.edges() && !joystick.host_actions(),"connection with held Shot must wait for neutral");
    raw->sample.pins=0xff;joystick.update(true);raw->sample.pins=0xcf;joystick.update(true);
    require(joystick.edges()==0x30 && joystick.host_actions()==0x820,"host button edges and Bomb domain");
    joystick.update(true);require(!joystick.edges(),"held controller repeated a menu confirmation");
    const auto count=raw->reads;joystick.update(false);
    require(raw->reads==count && !joystick.edges() && !joystick.host_actions(),"unfocused controller polled device");
    joystick.update(true);require(!joystick.edges(),"focus gain with held buttons invented a make");
    raw->sample.pins=0xff;joystick.update(true);raw->sample.pins=0xf7;joystick.update(true);
    require(joystick.edges()==8 && joystick.host_actions()==8,"neutral did not rearm controller");
    raw->sample.identity=18;joystick.update(true);require(!joystick.edges(),"replacement inherited old controller arm");
    raw->sample.pins=0xff;joystick.update(true);
    bool focused=true;unsigned phase=0;
    const unsigned groups[]{7,9,8,5,2,0,3,6};
    pc98_input::Latch latch;
    pc98_input::ByteSource keys{[&](auto){phase=0;},[&](unsigned group) {
        require(phase<8 && groups[phase++]==group,"composed keyboard byte order");return std::uint8_t(0);
    },[&]{require(phase++==8,"composed Shift order");raw->sample.pins=0xfd;return true;}};
    auto source=joystick.source(keys,[&]{return focused;});
    const auto before=raw->reads;
    auto physical=latch.poll(pc98_input::Operation::reset,source);
    require(phase==9 && raw->reads==before+1 && physical.joystick_pins==0xfd &&
        physical.joystick_enabled && latch.actions()==2 && latch.shift(),"joystick must read live pins after Shift");
    raw->sample.identity=-1;
    physical=latch.poll(pc98_input::Operation::sense,source);
    require(physical.joystick_enabled && physical.joystick_pins==0xff && latch.actions()==2,
        "unplug between enable and pin read must release pins without clearing Sense");
    const auto unplugged=raw->reads;latch.poll(pc98_input::Operation::reset,source);
    require(raw->reads==unplugged && !latch.actions(),"disabled controller performed a pin read");
    raw->sample={19,0xff};joystick.update(true);focused=false;const auto lost=raw->reads;
    physical=latch.poll(pc98_input::Operation::reset,source);
    require(!physical.joystick_enabled && raw->reads==lost,"focus loss at enable leaked a pin read");
    bool rejected=false;try{joystick.source(source,[]{return true;});}catch(const std::invalid_argument&){rejected=true;}
    require(rejected,"composition silently replaced an existing pin producer");
}
#ifdef _WIN32
struct State {unsigned calls=0;bool disconnected=false;JOYINFOEX value{};JOYCAPSA caps{};} s;
UINT WINAPI count(){return 2;}
MMRESULT WINAPI caps(UINT_PTR id,LPJOYCAPSA out,UINT size) {
    require(size==sizeof(*out),"WinMM caps size");if(id!=1)return MMSYSERR_NODRIVER;*out=s.caps;return 0;
}
MMRESULT WINAPI position(UINT id,LPJOYINFOEX out) {
    require(id==1 && out->dwSize==sizeof(*out) && out->dwFlags==
        (JOY_RETURNX|JOY_RETURNY|JOY_RETURNBUTTONS|JOY_RETURNPOV),"WinMM query contract");
    ++s.calls;if(s.disconnected)return JOYERR_UNPLUGGED;
    const auto size=out->dwSize,flags=out->dwFlags;*out=s.value;out->dwSize=size;out->dwFlags=flags;return 0;
}
j::Api fake(){return {&count,&caps,&position};}
void backend() {
    s.caps.wXmin=s.caps.wYmin=100;s.caps.wXmax=s.caps.wYmax=1100;
    s.caps.wNumAxes=2;s.caps.wNumButtons=2;s.caps.wCaps=JOYCAPS_HASPOV;
    s.value.dwXpos=s.value.dwYpos=600;s.value.dwPOV=JOY_POVCENTERED;
    auto device=j::platform_device(fake());require(device->read().pins==0xff,"WinMM calibrated neutral");
    s.value.dwXpos=1100;s.value.dwYpos=100;s.value.dwButtons=JOY_BUTTON1|JOY_BUTTON2;
    require(device->read().pins==0xc6,"WinMM axes and two buttons");
    s.value.dwXpos=s.value.dwYpos=600;s.value.dwButtons=0;
    const unsigned expected[]{1,9,8,10,2,6,4,5};
    for(unsigned i=0;i<8;++i){s.value.dwPOV=i*4500;require(device->read().pins==(0xff^expected[i]),"WinMM POV direction");}
    s.disconnected=true;require(device->read().identity<0,"WinMM unplug left stale pins");
    auto api=fake();api.position=nullptr;bool rejected=false;
    try{j::platform_device(api);}catch(const std::invalid_argument&){rejected=true;}require(rejected,"incomplete WinMM API");
}
#else
struct State {
    unsigned inits=0,quits=0,opens=0,closes=0,updates=0,reads=0;
    bool fail_init=false,fail_open=false,attached=true;
    int count=1,axes=2,hats=1,buttons=2,id=41;
    Sint16 x=0,y=0;Uint8 hat=0,buttons_value=0;
} s;
SDL_Joystick* handle(){return reinterpret_cast<SDL_Joystick*>(std::uintptr_t(1));}
int init(Uint32 flags){require(flags==SDL_INIT_JOYSTICK,"SDL joystick init scope");++s.inits;return s.fail_init?-1:0;}
void quit(Uint32 flags){require(flags==SDL_INIT_JOYSTICK,"SDL joystick quit scope");++s.quits;}
int count(){return s.count;}
SDL_Joystick* open(int index){require(index==0,"SDL joystick device index");++s.opens;return s.fail_open?nullptr:handle();}
void close(SDL_Joystick* p){require(p==handle(),"SDL close identity");++s.closes;}
void update(){++s.updates;}
SDL_bool attached(SDL_Joystick* p){require(p==handle(),"SDL attached identity");return s.attached?SDL_TRUE:SDL_FALSE;}
SDL_JoystickID identity(SDL_Joystick* p){require(p==handle(),"SDL instance identity");return s.id;}
int axes(SDL_Joystick*){return s.axes;}int hats(SDL_Joystick*){return s.hats;}int buttons(SDL_Joystick*){return s.buttons;}
Sint16 axis(SDL_Joystick* p,int i){require(p==handle() && i<s.axes && i<2,"SDL invalid axis read");++s.reads;return i?s.y:s.x;}
Uint8 hat(SDL_Joystick* p,int i){require(p==handle() && !i && s.hats>0,"SDL invalid hat read");++s.reads;return s.hat;}
Uint8 button(SDL_Joystick* p,int i){require(p==handle() && i<s.buttons && i<2,"SDL invalid button read");++s.reads;return (s.buttons_value>>i)&1;}
j::Api fake(){return {&init,&quit,&count,&open,&close,&update,&attached,&identity,&axes,&hats,&buttons,&axis,&hat,&button};}
void backend() {
    {auto device=j::platform_device(fake());require(device->read().pins==0xff,"SDL neutral");
     for(int value=-32768;value<=32767;++value) {
        s.x=Sint16(value);s.y=0;require(device->read().pins==(value<=-16384?0xfb:value>=16384?0xf7:0xff),"SDL complete X axis");
        s.x=0;s.y=Sint16(value);require(device->read().pins==(value<=-16384?0xfe:value>=16384?0xfd:0xff),"SDL complete Y axis");
     }
     s.x=s.y=0;
     for(unsigned bits=0;bits<16;++bits)for(unsigned buttons=0;buttons<4;++buttons) {
        s.hat=Uint8(bits);s.buttons_value=Uint8(buttons);
        const auto expected=((bits&1)?1:0)|((bits&4)?2:0)|((bits&8)?4:0)|((bits&2)?8:0)|
            ((buttons&1)?32:0)|((buttons&2)?16:0);
        require(device->read().pins==(0xff^expected),"SDL hat/button cross product");
     }
     s.axes=s.hats=s.buttons=0;const auto previous=s.reads;
     require(device->read().pins==0xff && s.reads==previous,"SDL missing controls must stay released");
     s.attached=false;s.count=0;require(device->read().identity<0 && s.closes==1,"SDL unplug ownership");
     s.attached=true;s.count=1;s.id=42;require(device->read().identity==42,"SDL reconnect instance");}
    require(s.closes==2 && s.quits==1,"SDL resource lifetime");
    s=State{};s.fail_init=true;{auto device=j::platform_device(fake());require(device->read().identity<0 && !s.opens,"SDL failed init");}
    require(!s.quits,"SDL quit without successful init");
    s=State{};s.fail_open=true;{auto device=j::platform_device(fake());require(device->read().identity<0,"SDL failed open");}
    require(!s.closes && s.quits==1,"SDL failed open cleanup");
    auto api=fake();api.axis=nullptr;const auto before=s.inits;bool rejected=false;
    try{j::platform_device(api);}catch(const std::invalid_argument&){rejected=true;}
    require(rejected && s.inits==before,"incomplete SDL API reached backend");
}
#endif
} // namespace
int main(int argc,char** argv){try{
#ifndef _WIN32
    if(argc==2 && std::string(argv[1])=="--pins") {
        auto device=j::platform_device(fake());
        for(unsigned bits=0;bits<16;++bits)for(unsigned buttons=0;buttons<4;++buttons) {
            s.hat=Uint8(bits);s.buttons_value=Uint8(buttons);
            std::cout<<bits<<' '<<buttons<<' '<<unsigned(device->read().pins)<<'\n';
        }
        return 0;
    }
#else
    (void)argv;
#endif
    require(argc==1,"unknown joystick contract option");
    composition();backend();std::cout<<"Host joystick production API, controls, focus/reconnect and live sampling PASS\n";return 0;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}

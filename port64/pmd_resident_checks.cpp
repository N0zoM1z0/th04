#include "sound_scenes.hpp"
#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <stdexcept>
using namespace th04::portable;
namespace {
void require(bool v,const char* text){if(!v)throw std::runtime_error(text);}
sound::Bytes song(){sound::Bytes b(26);for(unsigned p=0;p<12;++p)b[1+p*2]=24;b[25]=128;return b;}
sound::Bytes effects(){sound::Bytes b(257);for(unsigned p=0;p<128;++p)b[1+p*2]=1;b[256]=128;return b;}
void contracts(){
    auto resident=std::make_shared<sound::ResidentPmd>(sound::PmdProfile{});
    require(resident->command(0x900)==0x4800 && resident->command(0x800)==0x8ff && resident->command(0xa00)==255,"installed resident service state");
    unsigned efc=0,efs=0;std::vector<std::pair<unsigned,unsigned>> attribution;
    sound::Timeline timeline([&](const std::string& name)->std::optional<sound::Bytes>{
        if(name=="miko.efs"){++efs;return sound::Bytes{'4','4','0',' ','0',' '};}
        if(name=="miko.efc"){++efc;return effects();}return song();
    },{},{},resident,[&](auto p,auto g,const auto&){attribution.emplace_back(unsigned(p),g);});
    menu::Options options;options.bgm_mode=2;options.se_mode=2;
    timeline.enter(application::Program::op,1,options);timeline.op_title(false);
    require(timeline.bgm_active() && timeline.runtime()->control().bgm==1 && efs==1,"real mono driver capability and 8.3 routing");
    auto outgoing=timeline.runtime();
    {sound::Refresh wait(outgoing.get(),17730496);
        timeline.enter(application::Program::maine,2,options);
        require(outgoing->samples()==851 && attribution.back()==std::make_pair(unsigned(application::Program::op),1u),"drain outgoing refresh before process handoff");
        require(timeline.runtime()->beeper().count==0 && timeline.resident()==resident,"resident survives; MAINE beeper fresh");
    }
    const auto clock=resident->player().player().timers().cycles();
    options.se_mode=1;timeline.enter(application::Program::main,3,options);
    require(efc==1 && resident->player().player().timers().cycles()==clock,"new process does not restart resident clock");
    timeline.handle({sound::ActionKind::play,4});timeline.handle({sound::ActionKind::update});
    require(resident->player().player().player().effects().state().active,"actual resident EFC effect dispatch");
    timeline.enter(application::Program::maine,4,options);
    require(efc==1 && resident->player().player().player().effects().state().active,"MAINE retains resident EFC and active effect");
    timeline.runtime()->configure(0,1);
    require(!timeline.song_measure() && timeline.runtime()->command(0x500,0x1357)==0x1357,"off BGM preserves incoming AX without invented measures");
    bool rejected=false;try{resident->command(0xff00);}catch(const std::invalid_argument&){rejected=true;}
    require(rejected,"unrecovered service rejected");
    auto missing=std::make_shared<sound::ResidentPmd>(sound::PmdProfile{});
    sound::Runtime failed([](const std::string&)->std::optional<sound::Bytes>{return std::nullopt;},{},{},{},false,missing);
    failed.configure(2,0);rejected=false;
    try{sound::Refresh refresh(&failed,17730496);failed.handle({sound::ActionKind::load,0x600,"absent"});}
    catch(const std::runtime_error&){rejected=true;}
    require(rejected && !missing->file_open() && !missing->player().player().timers().cycles(),"resource failure closes typed file and cancels pending refresh during unwind");
    {sound::Refresh refresh(&failed,0);}
    std::cout<<"Resident PMD service/resource/lifetime, outgoing wait and real effect contracts PASS\n";
}
sound::Bytes read(const std::filesystem::path& p){std::ifstream f(p,std::ios::binary);require(bool(f),"resident input");return sound::Bytes(std::istreambuf_iterator<char>(f),{});}
std::string upper(std::string s){for(auto& c:s){require((c>='a'&&c<='z')||(c>='A'&&c<='Z')||(c>='0'&&c<='9')||c=='.'||c=='_',"resident 8.3 input name");if(c>='a'&&c<='z')c=char(c-'a'+'A');}return s;}
void sample(std::ostream& o,pmd::StereoSample v){for(auto s:{v.left,v.right}){o.put(char(std::uint16_t(s)&255));o.put(char(std::uint16_t(s)>>8));}}
void state(std::ostream& out,const sound::Timeline& t,std::uint16_t reply){
    const auto& r=*t.runtime();const auto& s=r.control();const auto& p=t.resident()->player();const auto& clock=p.player();
    out<<"STATE "<<unsigned(t.program())<<' '<<t.generation()<<' '<<reply<<' '<<+s.bgm<<' '<<+s.se<<' '<<+s.midi_possible<<' '<<+s.interrupt_if_midi<<' '<<+s.playing<<' '<<+s.frame<<' ';
    out<<std::hex<<std::setfill('0');for(auto c:s.filename)out<<std::setw(2)<<unsigned(c);out<<std::dec;
    out<<' '<<clock.timers().cycles()<<' '<<clock.fraction()<<' '<<p.pcm().samples()<<' '<<t.resident()->command(0x500)<<' '<<t.resident()->command(0x800)<<' '<<t.resident()->command(0xa00);
    for(const auto& bank:clock.player().music().registers())for(auto v:bank)out<<' '<<unsigned(v);out<<'\n';
}
}
int main(int argc,char** argv){try{
    if(argc==1){contracts();return 0;}
    require(argc==7,"resident PMD: resource board ROM operations trace PCM");
    const auto dir=std::filesystem::path(argv[1]).parent_path();const int board=std::stoi(argv[2]);require(board>=0&&board<=2,"resident board");
    std::ifstream ops(argv[4]);std::ofstream out(argv[5],std::ios::binary),pcm(argv[6],std::ios::binary);require(bool(ops)&&bool(out)&&bool(pcm),"resident output paths");
    char op;std::uint32_t hz;require(bool(ops>>op>>hz)&&op=='Q',"resident frequency");
    auto resident=std::make_shared<sound::ResidentPmd>(sound::PmdProfile{pmd::Board(board),hz,read(argv[3])});
    for(auto w:resident->installation())out<<"INSTALL "<<+w.bank<<' '<<+w.address<<' '<<+w.value<<'\n';
    sound::Timeline t([&](const std::string& name)->std::optional<sound::Bytes>{return read(dir/upper(name));},
        {},{},resident,[&](auto,auto,const auto& values){for(auto v:values)sample(pcm,v);},
        [&](auto p,auto g,const sound::Request& q){out<<"REQUEST "<<unsigned(p)<<' '<<g<<' '<<sound::kind_name(q.kind)<<' '<<q.a<<' '<<q.b<<' '<<(q.name.empty() ? "-" : q.name)<<'\n';});
    while(ops>>op){std::uint16_t reply=0;
        if(op=='T'){unsigned p,g,b,se;require(bool(ops>>p>>g>>b>>se)&&p<3,"resident process");menu::Options v;v.bgm_mode=std::uint8_t(b);v.se_mode=std::uint8_t(se);t.enter(application::Program(p),g,v);}
        else if(op=='L'){unsigned f;std::string name;require(bool(ops>>f>>name),"resident load");t.handle({sound::ActionKind::load,std::uint16_t(f),name});}
        else if(op=='K'){unsigned v;require(bool(ops>>v)&&v<=65535,"resident command");reply=t.runtime()->command(std::uint16_t(v),0x1357);}
        else if(op=='A'){std::uint64_t ns;require(bool(ops>>ns),"resident time");t.runtime()->advance(ns);}
        else if(op=='E'){unsigned v;require(bool(ops>>v)&&v<17,"resident effect");t.handle({sound::ActionKind::play,std::uint16_t(v)});}
        else if(op=='U'){unsigned v;require(bool(ops>>v)&&v<=1000,"resident update");while(v--)t.handle({sound::ActionKind::update});}
        else if(op=='Z')t.handle({sound::ActionKind::reset});
        else throw std::invalid_argument("resident operation");
        require(bool(t.runtime()),"resident requires a process");state(out,t,reply);
    }
    require(ops.eof(),"resident operation parse");out.close();pcm.close();require(bool(out)&&bool(pcm),"resident complete outputs");return 0;
}catch(const std::exception& e){std::cerr<<"Resident PMD: "<<e.what()<<'\n';return 1;}}

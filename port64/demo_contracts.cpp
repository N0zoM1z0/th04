#include "demo.hpp"
#include "main_state.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
using namespace th04::portable;
namespace {
void require(bool value,const char* message) {if(!value)throw std::runtime_error(message);}
score_file::Bytes read(const std::filesystem::path& path) {
    std::ifstream in(path,std::ios::binary);require(bool(in),"demo input missing");
    return {std::istreambuf_iterator<char>(in),{}};
}
score_file::Bytes unhex(const std::string& s) {
    score_file::Bytes b;if(s=="-")return b;
    require(!(s.size()%2),"odd demo hex vector");
    for(unsigned i=0;i<s.size();i+=2)b.push_back(std::uint8_t(std::stoul(s.substr(i,2),nullptr,16)));
    return b;
}
template<class T> void hex(const T& bytes) {
    const char* digits="0123456789abcdef";if(bytes.empty())std::cout<<'-';
    for(auto v:bytes)std::cout<<digits[unsigned(v)>>4]<<digits[unsigned(v)&15];
}
void next_demo(application::State& app,unsigned number) {
    require(number>=1 && number<=4,"demo number vector");
    for(unsigned i=1;i<=number;++i) {
        app.start_next_demo();if(i<number)app.return_from_main({});
    }
}
}
int main(int argc,char** argv) {
    try {
        if(argc>=3) {
            const std::string mode=argv[1];std::ifstream input(argv[2]);require(bool(input),"demo vectors missing");
            unsigned a,b,c,d,index=0;
            if(mode=="--replay" && argc==4) {
                std::vector<demo::Replay> replays;
                for(unsigned i=1;i<=4;++i)replays.emplace_back(read(std::filesystem::path(argv[3])/demo::Replay::filename(i)));
                while(input>>a>>b>>c>>d) {
                    require(a>=1 && a<=4 && b<=65535 && c<=65535 && d<=255,"demo sample vector");
                    const auto s=replays[a-1].sample(std::uint16_t(b),std::uint16_t(c),std::uint8_t(d));
                    std::cout<<s.input<<' '<<+s.shift<<' '<<s.replaced<<' '<<s.finished<<'\n';
                }
            } else if(mode=="--idle" && argc==3) {
                while(input>>a>>b>>c) {
                    require(a<=65535 && b<=1 && c<=65535,"demo idle vector");demo::Idle idle;
                    for(unsigned i=0;i<a;++i)require(!idle.tick(true,0),"options launched demo");
                    const bool start=idle.tick(b!=0,std::uint16_t(c));
                    std::cout<<start<<' '<<idle.count()<<'\n';
                }
            } else if(mode=="--op" && argc==3) {
                while(input>>a) {
                    require(a<=4,"OP replay rotation vector");application::State app;
                    for(unsigned i=0;i<a;++i){app.start_next_demo();app.return_from_main({});}
                    const auto generation=app.generation(),random=app.process_random_state();app.prepare_next_demo();
                    require(app.program()==application::Program::op && app.generation()==generation && app.process_random_state()==random,"demo replaced OP before fade");
                    const auto& r=app.resident();std::cout<<+r.stage<<' '<<+r.credit_lives<<' '<<+r.credit_bombs<<' '<<+r.demo_number
                        <<' '<<('0'+unsigned(r.playchar))<<' '<<+r.stage_ascii<<' '<<unsigned(r.shot_type)<<' '<<+r.demo_stage<<'\n';
                }
            } else if(mode=="--fade" && argc==3) {
                while(input>>a) {
                    demo::Fade fade(a);while(!fade.finished()) {
                        const int old=fade.published() ? fade.tone() : -1;
                        fade.advance();if(fade.published() && fade.tone()!=old)std::cout<<fade.ticks()<<' '<<fade.tone()<<'\n';
                    }
                    std::cout<<"END "<<fade.ticks()<<'\n';
                }
            } else if(mode=="--init" && argc==4) {
                const std::filesystem::path out(argv[3]);require(!std::filesystem::exists(out),"fresh demo init output required");std::filesystem::create_directories(out);
                unsigned present;std::string encoded;
                while(input>>a>>b>>c>>present>>encoded) {
                    const auto dir=out/std::to_string(index++);std::filesystem::create_directory(dir);
                    auto file=unhex(encoded);if(present){std::ofstream f(dir/"GENSOU.SCR",std::ios::binary);f.write(reinterpret_cast<const char*>(file.data()),file.size());}
                    application::State app;auto options=app.resident().config;options.rank=std::uint8_t(b);options.turbo=false;app.apply_options(options);
                    for(unsigned n=0;n<c;++n)app.advance_op_menu_frame();next_demo(app,a);
                    score_file::HostStore store(dir);gameplay::State main(app,gameplay::Mode::ordinary,{},&store);
                    const auto& r=app.resident();std::cout<<+main.rank()<<' '<<main.turbo()<<' '<<+main.score().power<<' '<<+main.scoreboard().performance
                        <<' '<<+r.stage<<' '<<+r.stage_ascii<<' '<<+r.config.rank<<' '<<r.config.turbo<<' ';
                    score_file::Bytes angles;for(const auto& spark:main.sparks().snapshot().entities){angles.push_back(std::uint8_t(spark.angle));angles.push_back(std::uint8_t(spark.angle>>8));}
                    std::cout<<app.process_random_state()<<' '<<main.random_cursor()<<' '<<+main.drop_cycle()<<' '<<main.hud_hp_previous()<<' ';
                    hex(main.scoreboard().digits);std::cout<<' ';hex(main.scoreboard().hiscore);std::cout<<' ';hex(main.random_ring_bytes());
                    std::cout<<' ';hex(angles);std::cout<<' ';hex(main.hud_text_plane().bytes());std::cout<<' ';hex(store.file().bytes());std::cout<<' '<<store.commits()<<'\n';
                    score_file::HostStore reopened(dir);require(reopened.file().bytes()==store.file().bytes(),"demo high-score writer not closed");
                }
            } else throw std::runtime_error("unknown demo vector mode");
            require(input.eof(),"malformed demo vectors");return 0;
        }
        demo::Idle idle;for(unsigned i=0;i<640;++i)require(!idle.tick(false,0),"demo started early");
        require(idle.tick(false,0x20),"frame640 input must not cancel the pending demo");
        demo::Replay replay(std::vector<std::uint8_t>(8000));require(replay.sample(3996,0,0).finished,"demo end boundary");
        require(replay.sample(65535,1,0).finished,"physical abort read replay out of bounds");
        application::State app;app.start_next_demo();gameplay::State main(app);
        require(main.rank()==2 && main.turbo() && main.score().power==128 && main.scoreboard().performance==20 && app.resident().stage==3,"demo initialization");
        std::cout<<"demo contracts PASS\n";return 0;
    } catch(const std::exception& error) {std::cerr<<error.what()<<'\n';return 1;}
}

#include "gameover.hpp"
#include "gameover_render.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif

namespace g=th04::portable::gameover;
namespace i=th04::portable::item;
namespace s=th04::portable::score;
namespace {
void require(bool b,const char* message) {if(!b)throw std::runtime_error(message);}
std::string hex(const std::string& text) {
    if(text.empty())return "-";
    constexpr char digits[]="0123456789abcdef";std::string result;
    for(unsigned char x:text) {result+=digits[x>>4];result+=digits[x&15];}
    return result;
}
void event(const g::Event& e) {
    std::cout<<int(e.kind)<<' '<<e.left<<' '<<e.row<<' '<<e.value<<' '<<e.attribute<<' '<<hex(e.text)<<'\n';
}
}
bool gameover_render_cli(int argc,char** argv) {
    if(argc!=3 || std::string(argv[1])!="--gameover-render")return false;
#ifdef _WIN32
    _setmode(_fileno(stdout),_O_BINARY);
#endif
    const auto directory=std::filesystem::path(argv[2]).parent_path();
    const auto read=[&](const char* name) {
        std::ifstream file(directory/name,std::ios::binary);require(bool(file),"Game Over render asset missing");
        return g::Renderer::Bytes(std::istreambuf_iterator<char>(file),{});
    };
    const auto gaiji=read("GAMEFT.BFT"),font=read("FREECG98.bmp");
    std::ifstream input(argv[2]);require(bool(input),"Game Over render fixture missing");
    std::unique_ptr<g::Renderer> renderer;std::string op;
    while(input>>op) {
        if(op=="CASE") {
            unsigned seed;require(bool(input>>seed),"missing render seed");
            g::Renderer::Bytes indices(256000),tram(8000);std::array<std::uint8_t,48> palette{};
            for(unsigned i=0;i<indices.size();++i)indices[i]=std::uint8_t((i*73+seed)&15);
            for(unsigned i=0;i<palette.size();++i)palette[i]=std::uint8_t(((i*29+seed)&15)<<4);
            constexpr unsigned attributes[]{0,1,0xe1,0x85,0x41,0x45};
            for(unsigned i=0;i<2000;++i) {
                tram[i*2]=std::uint8_t((i*31+seed)&127);
                tram[4000+i*2]=std::uint8_t(attributes[(i+seed)%6]);
            }
            renderer=std::make_unique<g::Renderer>(gaiji,font,std::move(indices),palette,th04::portable::registration::TextPlane(tram));
            continue;
        }
        require(bool(renderer),"Game Over render CASE missing");
        if(op=="SNAP") {
            int tone;require(bool(input>>tone),"missing Game Over snapshot tone");
            const auto rgb=renderer->rgb(tone),tram=renderer->text().bytes();
            for(const auto* data:{&renderer->indexed(),&tram,&rgb})std::cout.write(reinterpret_cast<const char*>(data->data()),data->size());
            continue;
        }
        g::Event e;
        if(op=="W" || op=="B")e.kind=op=="W" ? g::Kind::wipe : g::Kind::black;
        else {
            std::string encoded;
            require(op=="G" || op=="A","unknown Game Over render operation");
            require(bool(input>>e.left>>e.row>>e.value>>e.attribute>>encoded),"short Game Over render command");
            e.kind=op=="G" ? g::Kind::gaiji : g::Kind::ank;
            if(encoded!="-") {
                require(encoded.size()%2==0,"invalid Game Over text encoding");
                for(unsigned i=0;i<encoded.size();i+=2)e.text+=char(std::stoul(encoded.substr(i,2),nullptr,16));
            }
        }
        renderer->apply(e);
    }
    return true;
}
bool gameover_cli(int argc,char** argv) {
    if(argc!=3)return false;
    const bool scene_mode=std::string(argv[1])=="--gameover-scene";
    if(!scene_mode && std::string(argv[1])!="--gameover-menu")return false;
    std::ifstream input(argv[2]);require(bool(input),"Game Over fixture missing");
    unsigned stage,credit_lives,credit_bombs,initial;
    while(input>>stage>>credit_lives>>credit_bombs>>initial) {
        i::ScoreState resources;s::Snapshot board;
        const auto n=[&] {int value;require(bool(input>>value),"incomplete Game Over fixture");return value;};
        resources.power=n();resources.power_overflow=n();resources.dream_items_collected=n();
        resources.dream_score=n();resources.remaining_lives=n();resources.remaining_bombs=n();
        board.delta=n();board.frame_delta=n();board.unused=n();board.extends=n();board.hiscore_popup_shown=n();
        for(auto* bytes:{&board.digits,&board.hiscore,&board.temporary,&board.hud})for(auto& x:*bytes)x=n();
        resources.score_delta=board.delta;
        std::string sequence;require(bool(input>>sequence),"Game Over key sequence missing");
        unsigned clock=0;
        g::Context c{resources,board,std::uint8_t(stage),std::uint8_t(credit_lives),std::uint8_t(credit_bombs),
                     [&](const auto& e) {if(scene_mode)std::cout<<clock<<' ';event(e);},[]{}};
        if(scene_mode) {
            std::cout<<"BEGIN\n";g::Scene scene(c,initial);
            std::istringstream keys(sequence);std::string key;
            while(!scene.finished() && std::getline(keys,key,',')) {
                ++clock;scene.advance(std::uint16_t(std::stoul(key)));
            }
            require(scene.finished(),"Game Over scene never completed");
            const int route=scene.phase()==g::Phase::continue_run ? 0 : (scene.phase()==g::Phase::maine ? 1 : 2);
            std::cout<<"END "<<route<<' '<<clock<<' '<<scene.tone()<<' '<<int(resources.power)<<' '
                     <<int(resources.dream_items_collected)<<' '<<int(resources.remaining_lives)<<' '
                     <<int(resources.remaining_bombs)<<' '<<int(board.digits[0])<<'\n';
            continue;
        }
        std::cout<<"BEGIN\n";g::Menu menu(c,initial);
        std::istringstream keys(sequence);std::string key;
        while(menu.choice()==g::Choice::pending && std::getline(keys,key,',')) {
            menu.advance(std::uint16_t(std::stoul(key)));
            if(menu.choice()==g::Choice::pending)std::cout<<"FRAME "<<menu.ticks()-1<<' '<<menu.selected()<<' '<<menu.previous_input()<<'\n';
        }
        require(menu.choice()!=g::Choice::pending,"Game Over fixture never confirmed");
        std::cout<<"END "<<int(menu.choice())<<' '<<menu.selected()<<' '<<menu.ticks()<<' '<<menu.previous_input();
        std::cout<<' '<<int(resources.power)<<' '<<int(resources.dream_items_collected);
        std::cout<<' '<<resources.power_overflow<<' '<<resources.dream_score<<' '<<int(resources.remaining_lives)<<' '<<int(resources.remaining_bombs);
        for(const auto* bytes:{&board.digits,&board.hiscore,&board.temporary,&board.hud})for(auto x:*bytes)std::cout<<' '<<int(x);
        std::cout<<' '<<board.delta<<' '<<board.frame_delta<<' '<<int(board.unused)<<' '<<int(board.extends)<<' '<<int(board.hiscore_popup_shown)<<'\n';
    }
    return true;
}
void gameover_contracts() {
    i::ScoreState resources;resources.power=128;resources.dream_items_collected=7;
    resources.dream_score=1280;resources.remaining_lives=1;
    s::Snapshot board;board.digits[6]=1;board.hiscore[6]=2;
    unsigned saves=0;std::vector<g::Event> events;
    g::Context c{resources,board,0,3,2,[&](const auto& e){events.push_back(e);},[&]{++saves;}};
    g::Scene scene(c);
    require(scene.ticks()==0 && scene.phase()==g::Phase::initial_out,"Game Over construction consumed refresh");
    for(unsigned tick=0;tick<95;++tick)scene.advance(0);
    require(scene.phase()==g::Phase::release && scene.tone()==50,"Game Over fades/slide did not reach wait at95");
    for(unsigned tick=0;tick<120;++tick)scene.advance(0);
    require(scene.phase()==g::Phase::press && saves==0,"Game Over wait timed out");
    scene.advance(0x20);
    for(unsigned tick=0;tick<20;++tick)scene.advance(0x20);
    require(scene.phase()==g::Phase::menu && saves==0,"held acknowledgement accepted Continue");
    scene.advance(0);scene.advance(0);scene.advance(0x20);
    require(scene.phase()==g::Phase::final_out && saves==1 && board.digits[0]==1 &&
            board.digits[6]==0 && board.hiscore[6]==2 && resources.power==1 &&
            resources.dream_items_collected==0 && resources.dream_score==1280 &&
            resources.remaining_lives==3 && resources.remaining_bombs==2,
            "Continue lost ordered save/reset/retained state");
    for(unsigned tick=0;tick<68;++tick)scene.advance(0);
    require(scene.phase()==g::Phase::continue_run && scene.tone()==100,"Continue did not finish32+36 refreshes");
    board.digits[0]=3;g::Scene quit(c);
    for(unsigned tick=0;tick<95;++tick)quit.advance(0);
    quit.advance(0);quit.advance(0x20);
    require(quit.phase()==g::Phase::final_out,"credit exhaustion did not skip menu");
    for(unsigned tick=0;tick<32;++tick)quit.advance(0);
    require(quit.phase()==g::Phase::blackout,"quit omitted MAIN palette fade");
    for(unsigned tick=0;tick<68;++tick)quit.advance(0);
    require(!quit.finished(),"MAINE dispatch preceded69th fade refresh");
    quit.advance(0);require(quit.phase()==g::Phase::maine,"quit failed to request MAINE");
    c.stage=5;g::Scene final(c);
    require(final.phase()==g::Phase::bad_ending && final.ticks()==0,"Final Stage death did not directly dispatch Bad Ending");
    c.stage=6;g::Menu extra(c);require(extra.choice()==g::Choice::quit,"Extra exposed Continue");
    c.stage=0;board.digits[0]=0;c.save_continue=[] {throw std::runtime_error("write failure");};
    g::Menu failing(c);failing.advance(0);bool rejected=false;
    try {failing.advance(0x20);}catch(const std::runtime_error&) {rejected=true;}
    require(rejected && board.digits[0]==0 && failing.choice()==g::Choice::pending,"failed Continue save reset resources");
    std::cout<<"TH04 Game Over: PASS intro=95 continue_fades=68 quit_fade=69 stage5=BAD stage6=NO_CONTINUE\n";
}

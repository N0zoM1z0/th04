#include "cutscene.hpp"
#include "cutscene_scene.hpp"
#include "maine_ending.hpp"
#include "run_statistics.hpp"
#include <fstream>
#include <iostream>
#include <iterator>
#include <iomanip>
#include <stdexcept>
#include <sstream>
#include <set>

using namespace th04::portable;
namespace {
void require(bool value,const char* reason) { if(!value) throw std::runtime_error(reason); }
void event(const cutscene::Event& e) {
    std::cout<<cutscene::kind_name(e.kind)<<' '<<e.a<<' '<<e.b<<' '<<e.c<<' '<<e.d<<' '<<e.e<<' ';
    if(e.name.empty()) std::cout<<'-';
    else for(unsigned char c:e.name) std::cout<<std::hex<<std::setw(2)<<std::setfill('0')<<unsigned(c);
    std::cout<<std::dec<<'\n';
}
void trace(const char* path,unsigned held) {
    std::ifstream in(path,std::ios::binary);require(bool(in),"script input missing");
    cutscene::Bytes bytes((std::istreambuf_iterator<char>(in)),{});
    cutscene::Script script(std::move(bytes));script.begin();
    unsigned ticks=0;
    while(script.status()!=cutscene::Status::stopped && ++ticks<1000000) {
        // Original differential adapters complete waits at the consumer
        // boundary. Explicit release/press here does the same without
        // changing the next outer iteration's supplied held input.
        if(script.status()==cutscene::Status::release) script.advance(0,event);
        else if(script.status()==cutscene::Status::press) script.advance(0x20,event);
        else if(script.status()==cutscene::Status::measure) script.complete_measure_wait();
        else script.advance(static_cast<std::uint16_t>(held),event);
    }
    require(script.status()==cutscene::Status::stopped,"script did not terminate");
    std::cout<<"END "<<script.offset()<<' '<<script.x()<<' '<<script.y()<<' '<<script.interval()<<' '
             <<unsigned(script.color())<<' '<<script.weight()<<' '<<script.number_default()<<'\n';
}
cutscene::Bytes read(const std::string& path) {
    std::ifstream in(path,std::ios::binary);require(bool(in),"render asset missing");
    return cutscene::Bytes((std::istreambuf_iterator<char>(in)),{});
}
void write(const std::string& path,const cutscene::Bytes& bytes) {
    std::ofstream out(path,std::ios::binary);require(bool(out),"render output cannot open");
    out.write(reinterpret_cast<const char*>(bytes.data()),static_cast<std::streamsize>(bytes.size()));
    require(bool(out),"render output failed");
}
void render(const char* asset_dir,const char* name,unsigned held,const char* font_path,const char* checkpoints,const char* output) {
    const std::string directory(asset_dir),destination(output);
    cutscene::Assets assets;assets.font_bitmap=read(font_path);assets.gaiji=read(directory+"/GAMEFT.BFT");
    assets.scripts.emplace(name,read(directory+"/"+name));
    for(unsigned i=0;i<17;++i) {
        std::ostringstream filename;filename<<"ED"<<std::setw(2)<<std::setfill('0')<<i<<".PI";
        assets.pictures.emplace(filename.str(),decode_pi(read(directory+"/"+filename.str())));
    }
    cutscene::Scene scene(assets,name);
    std::ifstream positions(checkpoints);require(bool(positions),"render checkpoints missing");
    std::set<unsigned> captures;unsigned n;
    while(positions>>n) captures.insert(n);
    require(!captures.empty(),"render checkpoints are empty");
    std::ofstream states(destination+"/states.txt");require(bool(states),"render states cannot open");
    unsigned index=0,ticks=0;
    const auto observe=[&](const cutscene::Event&) {
        if(captures.count(index)) {
            write(destination+"/"+std::to_string(index)+"-0.bin",scene.page(0));
            write(destination+"/"+std::to_string(index)+"-1.bin",scene.page(1));
            write(destination+"/"+std::to_string(index)+".pal",cutscene::Bytes(scene.palette().begin(),scene.palette().end()));
            states<<index<<' '<<scene.shown_page()<<' '<<scene.access_page()<<' '<<scene.scroll()<<' '<<scene.script().tone()<<'\n';
            captures.erase(index);
        }
        ++index;
    };
    while(scene.script().status()!=cutscene::Status::stopped && ++ticks<1000000) {
        if(scene.script().status()==cutscene::Status::release) scene.advance(0,observe);
        else if(scene.script().status()==cutscene::Status::press) scene.advance(0x20,observe);
        else if(scene.script().status()==cutscene::Status::measure) scene.script().complete_measure_wait();
        else scene.advance(static_cast<std::uint16_t>(held),observe);
    }
    require(scene.script().status()==cutscene::Status::stopped && captures.empty(),"render did not reach every checkpoint");
    std::cout<<"Rendered "<<name<<" events="<<index<<" ticks="<<ticks<<'\n';
}
void glyphs(const char* font_path,const char* fixtures,const char* output) {
    cutscene::Assets assets;assets.font_bitmap=read(font_path);assets.scripts.emplace("TEST",cutscene::Bytes{'\\','$'});
    std::ifstream input(fixtures);require(bool(input),"glyph fixtures missing");
    unsigned weight,color,x,y,glyph,index=0;
    while(input>>weight>>color>>x>>y>>glyph) {
        cutscene::Scene scene(assets,"TEST");
        scene.apply({cutscene::Kind::text,int(x),int(y),int(glyph),int(color),int(weight)});
        write(std::string(output)+"/glyph-"+std::to_string(index++)+".bin",scene.page(0));
    }
    require(index>0,"no glyph fixtures");
    std::cout<<"Original font-effect controls: "<<index<<" fixtures\n";
}
void decode(const char* image,const char* output) {
    const auto pi=decode_pi(read(image));cutscene::Bytes data;
    for(unsigned value:{pi.width,pi.height}) for(unsigned i=0;i<4;++i) data.push_back(static_cast<std::uint8_t>(value>>(i*8)));
    data.insert(data.end(),pi.palette.begin(),pi.palette.end());data.insert(data.end(),pi.pixels.begin(),pi.pixels.end());
    write(output,data);
}
cutscene::Bytes blank_test_font() {
    // Synthetic empty CGROM bitmap for control-only public tests. Pixel
    // differentials use the user's supplied real font independently.
    cutscene::Bytes bitmap(62+524288);
    const auto word=[&](unsigned at,unsigned value) { bitmap[at]=value&255;bitmap[at+1]=(value>>8)&255; };
    word(0,0x4d42);word(10,62);word(14,40);word(18,2048);word(22,2048);word(26,1);word(28,1);
    return bitmap;
}
void ending_contracts() {
    require(maine::input_from_main_actions(0x10)==0x20,"MAIN Z must not become MAINE Escape");
    require(maine::input_from_main_actions(0x2000)==0x10,"MAIN Escape translates to MAINE Escape");
    for(unsigned character=0;character<2;++character) for(unsigned shot=0;shot<2;++shot)
        for(bool bad:{false,true}) {
            application::State app;app.start_normal(static_cast<application::Playchar>(character),
                static_cast<application::ShotType>(shot));
            const auto generation=app.generation(),random=app.process_random_state();
            application::RunStatistics stats;stats.score_digits={1,2,3,4,5,6,7,8};stats.frames=123456;
            cutscene::Assets assets;assets.font_bitmap=blank_test_font();const auto name=cutscene::script_name(character,shot,bad);
            assets.scripts.emplace(name,cutscene::Bytes{'\\','$'});
            unsigned releases=0;
            maine::Ending ending(app,stats,bad ? application::EndSequence::bad : application::EndSequence::good,
                assets,[&] {
                    require(app.program()==application::Program::main && app.generation()==generation,
                        "MAIN resources released after entering MAINE");
                    require(app.resident().score_digits==stats.score_digits && app.resident().statistics.frames==stats.frames,
                        "MAIN resources released before publication");
                    require(app.process_random_state()==random,"MAIN random state reseeded before release");
                    ++releases;
                });
            require(ending.main_sound_requests().size()==1 && ending.main_sound_requests()[0].a==0x204,"MAIN omitted song fade4 request");
            require(app.resident().end_sequence==(bad ? application::EndSequence::bad : application::EndSequence::good) &&
                app.resident().end_type_ascii==(bad ? '1' : '0'),"Ending metadata was not written before fade");
            for(unsigned tick=1;tick<=273;++tick) {
                ending.advance(cutscene::input_cancel);
                if(tick<273) require(app.generation()==generation && !releases && !ending.scene(),
                    "Escape skipped MAIN's fade or replaced its resources early");
            }
            require(ending.main_tone()==0 && ending.fade_ticks()==273 && releases==1 &&
                app.generation()==generation+1 && app.program()==application::Program::maine &&
                app.process_random_state()==1 && ending.script_name()==name,"MAINE lifecycle boundary differs");
            ending.advance(0);
            require(ending.phase()==maine::Phase::staff_roll_pending,"script termination must reach Staff Roll owner");
            for(unsigned i=0;i<20;++i) ending.advance(0x30);
            require(app.generation()==generation+1 && releases==1,"completed Ending repeated execl/release");
        }
    for(unsigned fallback:{0u,1u,4u,999u}) for(bool active:{false,true}) {
        application::State app;app.start_normal(application::Playchar::reimu,application::ShotType::a);
        cutscene::Assets assets;assets.font_bitmap=blank_test_font();std::ostringstream text;text<<"\\wm3,"<<fallback<<"\\$";
        const auto body=text.str();assets.scripts.emplace("_ED000.TXT",cutscene::Bytes(body.begin(),body.end()));
        maine::Ending ending(app,{},application::EndSequence::good,assets,{},active);
        for(unsigned i=0;i<273;++i) ending.advance(0);
        for(unsigned i=0;i<100 && ending.scene()->script().status()!=cutscene::Status::measure &&
                ending.phase()!=maine::Phase::staff_roll_pending;++i) ending.advance(0);
        if(active) {
            require(ending.scene()->script().status()==cutscene::Status::measure,"active song did not own wait");
            for(unsigned i=0;i<1000;++i) ending.advance(0x30);
            require(ending.scene()->script().status()==cutscene::Status::measure,"keys or time fabricated song progress");
            ending.report_song_measure(2);ending.advance(0);
            require(ending.scene()->script().status()==cutscene::Status::measure,"song resumed before measure3");
            ending.report_song_measure(3);ending.advance(0);
        } else if(fallback) {
            require(ending.scene()->script().status()==cutscene::Status::measure,"inactive sound omitted fallback");
            for(unsigned i=1;i<fallback;++i) {
                ending.advance(0x20);
                require(ending.scene()->script().status()==cutscene::Status::measure,"inactive fallback finished early");
            }
            ending.advance(0x20);
        }
        require(ending.phase()==maine::Phase::staff_roll_pending,"sound wait failed to resume script");
    }
    std::cout<<"MAIN-to-MAINE lifecycle/input/sound contracts: PASS\n";
}
void handoff(const char* fixtures) {
    std::ifstream input(fixtures);require(bool(input),"handoff fixtures missing");
    unsigned bad;std::uint16_t standard,spawned,collected,point,max,gone,killed;
    std::uint32_t slow,total,pending;
    while(input>>bad>>standard>>spawned>>collected>>point>>max>>gone>>killed>>slow>>total>>pending) {
        score::Snapshot board;board.delta=pending;
        unsigned digit;for(auto& d:board.digits) {require(bool(input>>digit),"truncated score digits");d=static_cast<std::uint8_t>(digit);}
        item::ScoreState awards;awards.items_collected=collected;awards.total_point_items_collected=point;
        awards.max_valued_point_items=max;
        gameplay::FrameCounts frames{standard,slow,total};
        const auto stats=gameplay::run_statistics(board,awards,spawned,gone,killed,frames);
        application::State app;app.start_normal(application::Playchar::reimu,application::ShotType::a);
        cutscene::Assets assets;assets.font_bitmap=blank_test_font();const auto name=cutscene::script_name(0,0,bad);
        assets.scripts.emplace(name,cutscene::Bytes{'\\','$'});
        maine::Ending ending(app,stats,bad ? application::EndSequence::bad : application::EndSequence::good,assets);
        for(unsigned i=0;i<273;++i)ending.advance(0);
        const auto& r=app.resident();const auto& s=r.statistics;
        std::cout<<unsigned(r.end_sequence)<<' '<<unsigned(r.end_type_ascii)<<' '<<s.std_frames<<' '<<s.items_spawned<<' '
            <<s.items_collected<<' '<<s.point_items_collected<<' '<<s.max_valued_point_items_collected<<' '
            <<s.enemies_gone<<' '<<s.enemies_killed<<' '<<s.slow_frames<<' '<<s.frames;
        for(auto d:r.score_digits)std::cout<<' '<<unsigned(d);
        std::cout<<' '<<board.delta<<'\n';
    }
}
void frame_counts(const char* fixtures) {
    std::ifstream input(fixtures);require(bool(input),"frame fixtures missing");
    std::uint32_t slow,total;std::uint16_t refreshes,threshold;
    while(input>>slow>>total>>refreshes>>threshold) {
        gameplay::FrameCounts counts{0,slow,total};counts.complete(refreshes,threshold);
        std::cout<<counts.slow<<' '<<counts.total<<'\n';
    }
}
void fade_trace() {
    application::State app;app.start_normal(application::Playchar::reimu,application::ShotType::a);
    cutscene::Assets assets;assets.font_bitmap=blank_test_font();assets.scripts.emplace("_ED000.TXT",cutscene::Bytes{'\\','$'});
    maine::Ending ending(app,{},application::EndSequence::good,assets);
    int previous=ending.main_tone();
    for(unsigned tick=1;tick<=273;++tick) {
        ending.advance(cutscene::input_cancel);
        if(tick==1 || ending.main_tone()!=previous)std::cout<<tick<<' '<<ending.main_tone()<<'\n';
        previous=ending.main_tone();
    }
}
void contracts() {
    ending_contracts();
    require(cutscene::script_name(0,0,false)=="_ED000.TXT","Reimu A good route");
    require(cutscene::script_name(1,1,true)=="_ED111.TXT","Marisa B bad route");
    cutscene::Script script({'\\','k','2','\\','$'});script.begin();
    script.advance(0,{});require(script.status()==cutscene::Status::release,"wait releases first");
    for(unsigned i=0;i<30;++i) script.advance(0x20,{});
    require(script.status()==cutscene::Status::release,"release cannot time out");
    script.advance(0,{});require(script.status()==cutscene::Status::press,"release advances to press");
    script.advance(0,{});require(script.status()==cutscene::Status::press,"press budget retains first frame");
    script.advance(0,{});require(script.status()==cutscene::Status::running,"finite press budget expires");
    script.advance(0,{});require(script.status()==cutscene::Status::stopped,"stop owns cleanup");
    cutscene::Script fast({'\\','w','m','3',',','4','\\','$'});fast.begin();fast.advance(cutscene::input_cancel,{});
    require(fast.status()==cutscene::Status::stopped,"Escape skips measure waits");
    cutscene::Script music({'\\','w','m','3',',','4','\\','$'});music.begin();music.advance(0,{});
    require(music.status()==cutscene::Status::delay,"box mask delays precede music wait");
    for(unsigned i=0;i<20 && music.status()!=cutscene::Status::measure;++i) music.advance(0,{});
    require(music.status()==cutscene::Status::measure,"music owner holds measure boundary");
    for(unsigned i=0;i<100;++i) music.advance(0x20,{});
    require(music.status()==cutscene::Status::measure,"key input is not song progress");
    music.complete_measure_wait();music.advance(0,{});
    require(music.status()==cutscene::Status::stopped,"explicit sound progress resumes script");
    bool malformed=false;
    try { cutscene::Script bad({0x82});bad.begin();bad.advance(0,{}); }
    catch(const std::invalid_argument&) { malformed=true; }
    require(malformed,"native buffer bounds reject truncated glyphs");
    std::cout<<"MAINE cutscene lifecycle contracts: PASS\n";
}
}
int main(int argc,char** argv) {
    try {
        if(argc==4 && std::string(argv[1])=="--trace") trace(argv[2],std::stoul(argv[3]));
        else if(argc==4 && std::string(argv[1])=="--decode") decode(argv[2],argv[3]);
        else if(argc==8 && std::string(argv[1])=="--render") render(argv[2],argv[3],std::stoul(argv[4]),argv[5],argv[6],argv[7]);
        else if(argc==5 && std::string(argv[1])=="--glyphs") glyphs(argv[2],argv[3],argv[4]);
        else if(argc==3 && std::string(argv[1])=="--handoff") handoff(argv[2]);
        else if(argc==3 && std::string(argv[1])=="--frames") frame_counts(argv[2]);
        else if(argc==2 && std::string(argv[1])=="--fade") fade_trace();
        else if(argc==1) contracts();
        else throw std::invalid_argument("usage: cutscene-contracts [--trace SCRIPT HELD | --render ASSETS SCRIPT HELD FONT CHECKPOINTS OUTPUT]");
        return 0;
    } catch(const std::exception& error) { std::cerr<<error.what()<<'\n';return 1; }
}

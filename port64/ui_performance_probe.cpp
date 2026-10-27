// Muted component probe. Loose PAR assets are extracted and pinned by the runner;
// its --hdi argument identifies that source image, not a product boot scenario.
#include "registration_scene.hpp"
#include "host_score.hpp"
#include "random_lcg.hpp"
#include <chrono>
#include <filesystem>
#include <fstream>
#include <iostream>

namespace fs=std::filesystem;
namespace p=th04::portable;
using Clock=std::chrono::steady_clock;
using Bytes=std::vector<std::uint8_t>;
static auto ns(){return std::chrono::duration_cast<std::chrono::nanoseconds>(Clock::now().time_since_epoch()).count();}
static Bytes read(const fs::path& path){std::ifstream f(path,std::ios::binary);if(!f)throw std::runtime_error("missing probe input");return {std::istreambuf_iterator<char>(f),{}};}
static void write(std::ostream& f,const Bytes& b){f.write(reinterpret_cast<const char*>(b.data()),std::streamsize(b.size()));}
int main(int argc,char** argv)try{
    std::map<std::string,std::string> args;
    for(int i=1;i<argc;++i){std::string k=argv[i];if(k=="--mute")continue;if(i+1>=argc)throw std::runtime_error("missing argument");args[k]=argv[++i];}
    const fs::path root=fs::absolute(argv[0]).parent_path()/"ui-assets",out=args.at("--ui-performance-checks");
    if(fs::exists(out))throw std::runtime_error("fresh outputs required");fs::create_directories(out);
    p::registration::GraphicsAssets assets;
    assets.graphics.font_bitmap=read(args.at("--font-bmp"));assets.graphics.gaiji=read(root/"GAMEFT.BFT");
    assets.numerals=read(root/"SCNUM2.BFT");
    for(const auto& file:fs::directory_iterator(root)){
        const auto name=file.path().filename().string();
        if(file.path().extension()==".PI")assets.graphics.pictures.emplace(name,decode_pi(read(file.path())));
        else if(file.path().extension()==".TXT")assets.graphics.scripts.emplace(name,read(file.path()));
    }
#ifdef TH04_FONT_ROW_CHECKS
    p::dialog::Font font(assets.graphics.font_bitmap);
    for(unsigned c=0;c<65536;++c)for(unsigned y=0;y<17;++y){
        const auto bits=font.row(std::uint16_t(c),y);
        for(unsigned x=0;x<16;++x)if(bool(bits&(0x8000u>>x))!=font.pixel(std::uint16_t(c),x,y))throw std::runtime_error("font row mismatch");
    }
    for(unsigned c=0;c<256;++c)for(unsigned y=0;y<17;++y)for(unsigned x=0;x<8;++x)
        if(bool(font.ank_row(std::uint8_t(c),y)&(128u>>x))!=font.ank_pixel(std::uint8_t(c),x,y))throw std::runtime_error("ANK row mismatch");
    std::ofstream(out/"font-rows-passed.txt")<<"65536 codes, 17 rows, 16 pixels; 256 ANK codes, 17 rows, 8 pixels\n";
#endif
    std::ofstream costs(out/"costs.tsv"),state(out/"state.tsv"),io(out/"io.tsv"),pictures(out/"registration.bin",std::ios::binary);
    costs<<"scene tick advance_ns redraw_ns\n";io<<"duration_ns commits\n";
    p::score_file::HostStore store(out/"save");p::rng::Lcg32 random;
    p::registration::Run run;run.stage=5;run.rank=1;run.turbo=1;run.digits[6]=1;
    p::registration::Scene scene(assets,run,store.file(),[&]{return random.next15();},0,[&](const auto& op){auto begin=ns();store.apply(op);io<<ns()-begin<<' '<<store.commits()<<'\n';});
    for(unsigned tick=0;tick<240;++tick){
        std::uint16_t held=0;
        if(tick>=40 && tick<46)held=p::registration::right;
        if(tick>=60 && tick<130)held=p::registration::right;
        if(tick>=140 && tick<146)held=p::registration::down;
        if(tick>=160 && tick<166)held=p::registration::shot;
        if(tick==210)held=p::registration::cancel;
        const auto begin=ns();scene.advance(held);const auto advanced=ns();auto rgb=scene.renderer().rgb(0,scene.tone());const auto rendered=ns();
        costs<<"registration "<<tick<<' '<<advanced-begin<<' '<<rendered-advanced<<'\n';
        state<<tick<<' '<<int(scene.status())<<' '<<scene.menu().alphabet_column()<<' '<<scene.menu().alphabet_row()<<' '<<scene.menu().name_cursor()<<' '<<unsigned(scene.menu().repeat_frames())<<'\n';
        if(tick%20==0 || tick==239){write(pictures,rgb);write(pictures,scene.renderer().text_plane().bytes());}
    }
    if(!scene.finished() || !store.commits())throw std::runtime_error("registration did not save/finish");
    unsigned scripts=0;
    for(const auto& [name,script]:assets.graphics.scripts){
        if(name.rfind("_ED",0)!=0)continue;
        ++scripts;p::cutscene::Scene story(assets.graphics,name);std::ofstream frames(out/(name+".bin"),std::ios::binary);
        for(unsigned tick=0;tick<20000;++tick){
            // This graphics fixture bypasses only PMD measure waits. Real
            // Windows Ending integration separately executes its sound clock.
            if(story.script().status()==p::cutscene::Status::measure)story.script().complete_measure_wait();
            auto before=story.script().status();auto begin=ns();story.advance(tick%12<6 ? 0x20 : 0);auto end=ns();
            costs<<name<<' '<<tick<<' '<<end-begin<<" 0\n";
            state<<name<<' '<<tick<<' '<<int(story.script().status())<<' '<<story.script().offset()<<'\n';
            if(tick%200==0 || before!=story.script().status()){
                write(frames,story.page(0));write(frames,story.page(1));
                const auto& palette=story.palette();frames.write(reinterpret_cast<const char*>(palette.data()),palette.size());
            }
            if(story.script().status()==p::cutscene::Status::stopped)break;
            if(tick==19999)throw std::runtime_error("Ending script did not finish");
        }
    }
    if(scripts!=8)throw std::runtime_error("expected eight Ending scripts");
    std::cout<<"PASS registration editing/save and eight Ending graphics scripts\n";
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}

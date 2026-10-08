#include "registration_scene.hpp"
#include "host_score.hpp"
#include "random_lcg.hpp"
#include "application_state.hpp"
#include <chrono>
#include <fstream>
#include <iostream>
#include <stdexcept>

namespace r=th04::portable::registration;
namespace sf=th04::portable::score_file;
namespace rng=th04::portable::rng;
namespace app=th04::portable::application;
namespace fs=std::filesystem;
namespace {
void require(bool b,const char* message) {if(!b)throw std::runtime_error(message);}
sf::Bytes read(const fs::path& path) {
    std::ifstream in(path,std::ios::binary);require(bool(in),"test input missing");
    return {std::istreambuf_iterator<char>(in),{}};
}
void write(const fs::path& path,const sf::Bytes& data) {
    std::ofstream out(path,std::ios::binary);
    out.write(reinterpret_cast<const char*>(data.data()),std::streamsize(data.size()));
    require(bool(out),"test write failed");
}
r::GraphicsAssets synthetic() {
    // Public control assets; actual PI/BFNT/CGROM pixels have a separate
    // independent original-instruction differential.
    r::GraphicsAssets assets;assets.graphics.font_bitmap.resize(62+524288);
    const auto word=[&](unsigned at,unsigned value) {
        assets.graphics.font_bitmap[at]=sf::Byte(value);
        assets.graphics.font_bitmap[at+1]=sf::Byte(value>>8);
    };
    word(0,0x4d42);word(10,62);word(14,40);word(18,2048);word(22,2048);word(26,1);word(28,1);
    assets.graphics.gaiji.resize(32+256*32,0xff);
    assets.graphics.gaiji[28]=assets.graphics.gaiji[29]=0;
    PiImage pi;pi.width=640;pi.height=400;pi.pixels.resize(128000,0x33);
    pi.palette.fill(0xf0);assets.graphics.pictures.emplace("HI01.PI",std::move(pi));
    assets.numerals.resize(32+20*128);
    const char header[]="BFNT";
    std::copy(header,header+4,assets.numerals.begin());
    assets.numerals[4]=26;assets.numerals[5]=3;
    assets.numerals[8]=16;assets.numerals[10]=16;assets.numerals[14]=19;
    assets.non_turbo_message="NO RANKING";
    return assets;
}
void release(r::Scene& scene) {scene.advance(0);scene.advance(0);}
void press(r::Scene& scene,std::uint16_t key) {release(scene);scene.advance(key);}
void fade_in(r::Scene& scene,std::uint16_t held=0) {
    require(scene.ticks()==0 && scene.tone()==0,"scene construction consumed a refresh");
    const auto before=scene.menu().ticks();
    for(unsigned tick=1;tick<=34;++tick) {
        scene.advance(held);
        require(scene.status()==r::Status::fade_in && scene.menu().ticks()==before,
                "keyboard/save escaped startup fade");
        require(scene.tone()==int((tick-1)/2)*6,"startup six-tone schedule differs");
    }
    scene.advance(held);require(scene.tone()==100,"black-in did not finish on refresh35");
}
void fade_out(r::Scene& scene) {
    require(scene.status()==r::Status::fade_out,"registration omitted final blackout");
    for(unsigned tick=1;tick<=17;++tick) {
        scene.advance(0);require(!scene.finished(),"blackout returned early");
        require(scene.tone()==100-int(tick-1)*6,"blackout six-tone schedule differs");
    }
    scene.advance(0);require(scene.finished() && scene.tone()==0,"blackout did not finish on refresh18");
    const auto ticks=scene.ticks();scene.advance(r::shot);
    require(scene.ticks()==ticks,"completed scene advanced");
}
void contracts(const r::GraphicsAssets& assets,const fs::path& root) {
    require(r::input_from_main_actions(0x20)==r::shot &&
        r::input_from_main_actions(0x800)==r::bomb &&
        r::input_from_main_actions(0x1000)==r::ok &&
        r::input_from_main_actions(0x2000)==r::cancel &&
        r::input_from_main_actions(15)==15,"explicit host key mapping differs");
    unsigned cases=0;
    for(unsigned character=0;character<2;++character)for(unsigned rank=0;rank<5;++rank) {
        const auto directory=root/("section-"+std::to_string(character*5+rank));
        sf::HostStore store(directory);rng::Lcg32 random(318);unsigned draws=0;
        r::Run run;run.stage=rank==4 ? 6 : 5;run.rank=sf::Byte(rank);
        run.character_ascii=sf::Byte('0'+character);run.shot_type=sf::Byte(character);
        run.end_sequence=rank==4 ? 0xfd : 0xff;run.digits[6]=1;
        r::Scene scene(assets,run,store.file(),[&] {++draws;return random.next15();},r::shot,
            [&](const auto& op) {store.apply(op);});
        require(store.commits()==1 && draws==20,"missing file did not recreate at writer close");
        const auto initial=read(store.path());
        require(initial.size()==1960 && scene.menu().editable(),"ten-section recreation differs");
        fade_in(scene,r::shot);
        for(unsigned i=0;i<40;++i)scene.advance(r::shot);
        require(scene.menu().name_cursor()==0 && store.commits()==1,
                "inherited confirmation typed a name");
        // The original initial lock is1, so changing the held key does not
        // unlock it. Only a complete two-sample release permits a new key.
        press(scene,r::shot);
        require(scene.menu().name_cursor()==1,"released Shot did not type");
        press(scene,r::bomb);
        require(scene.menu().name_cursor()==0,"Bomb did not erase/back");
        press(scene,r::ok);
        press(scene,r::cancel);
        require(store.commits()==2 && draws==42 && read(store.path())==store.file().bytes(),
                "Esc did not persist the partial name at save close");
        fade_out(scene);
        sf::HostStore restart(directory);sf::Section decoded{};
        sf::load_for(decoded,restart.file(),sf::Byte(character),sf::Byte(rank),[&] {return random.next15();});
        require(decoded[4]==0xaa && decoded[5]==r::empty && decoded[174]==(character ? 2 : 1),
                "fresh host store lost name/clear bit");
        for(unsigned index=0;index<10;++index) {
            sf::Section section{};
            sf::load_for(section,restart.file(),sf::Byte(index/5),sf::Byte(index%5),[&] {return random.next15();});
            // A successful load consumes no recreation/writes; all ten
            // sections were independently checksum-valid on reload.
            require(!restart.file().changed(),"saved nonselected section is corrupt");
        }
        // Rendering/repaint is const and cannot consume RNG or a refresh.
        const auto ticks=scene.ticks(),seed=random.state();
        const auto picture=scene.renderer().rgb(0,scene.tone());
        require(picture.size()==768000 && scene.ticks()==ticks && random.state()==seed,
                "repaint changed scene/RNG");
        ++cases;
    }
    // Eight characters move to the explicit Enter cell; another fresh Shot
    // confirms. Eight characters alone must not automatically save.
    {
        sf::HostStore store(root/"full-name");rng::Lcg32 random;
        r::Run run;run.stage=5;run.digits[6]=1;
        r::Scene scene(assets,run,store.file(),[&] {return random.next15();},0,
            [&](const auto& op){store.apply(op);});
        fade_in(scene);
        for(unsigned i=0;i<8;++i)press(scene,r::shot);
        require(scene.status()==r::Status::editing && scene.menu().alphabet_column()==16 &&
                scene.menu().alphabet_row()==2 && store.commits()==1,"full name saved before Enter");
        press(scene,r::shot);fade_out(scene);
        sf::HostStore restart(root/"full-name");sf::Section decoded{};
        sf::load_for(decoded,restart.file(),0,0,[&] {return random.next15();});
        for(unsigned i=0;i<8;++i)require(decoded[4+i]==0xaa,"full name reload differs");
        ++cases;
    }
    for(unsigned corrupt=0;corrupt<3;++corrupt) {
        const auto directory=root/("no-entry-"+std::to_string(corrupt));
        fs::create_directories(directory);
        if(corrupt==1)write(directory/"GENSOU.SCR",sf::Bytes{1,2,3});
        if(corrupt==2) {
            sf::File initial;rng::Lcg32 seed;sf::Section section{};
            sf::recreate(section,initial,[&] {return seed.next15();});
            auto bytes=initial.bytes();
            for(unsigned index=0;index<10;++index)bytes[index*196+2]^=1;
            write(directory/"GENSOU.SCR",bytes);
        }
        sf::HostStore store(directory);rng::Lcg32 random;unsigned draws=0;
        r::Run run;run.rank=1;run.turbo=0;
        r::Scene scene(assets,run,store.file(),[&] {++draws;return random.next15();},r::ok,
            [&](const auto& op){store.apply(op);});
        require(draws==20 && store.commits()==1,"bad selected file recreation differs");
        fade_in(scene,r::ok);
        require(scene.status()==r::Status::release && store.commits()==2 && draws==42,
                "no-entry save did not follow complete fade");
        for(unsigned i=0;i<100;++i)scene.advance(r::ok);
        require(scene.status()==r::Status::release,"held key bypassed acknowledgement release");
        scene.advance(0);require(scene.status()==r::Status::release,"OR sample lost preceding held key");
        scene.advance(0);require(scene.status()==r::Status::press,"complete release did not enter press");
        for(unsigned i=0;i<100;++i)scene.advance(0);
        require(scene.status()==r::Status::press,"wait0 timed out");
        scene.advance(r::ok);fade_out(scene);++cases;
    }
    // A valid below-table score follows the same acknowledgement path without
    // recreating. Retain arbitrary bytes after the ten sections across save.
    {
        const auto directory=root/"below-table";fs::create_directories(directory);
        sf::File seedfile;rng::Lcg32 random;sf::Section section{};
        sf::recreate(section,seedfile,[&] {return random.next15();});
        auto bytes=seedfile.bytes();bytes.push_back(0x61);bytes.push_back(0x7f);
        write(directory/"GENSOU.SCR",bytes);sf::HostStore store(directory);
        r::Run run;run.rank=2;
        r::Scene scene(assets,run,store.file(),[&] {return random.next15();},0,
            [&](const auto& op){store.apply(op);});
        require(!scene.menu().editable() && store.commits()==0,"below-table valid load recreated");
        fade_in(scene);require(store.commits()==1,"below-table score was not saved");
        release(scene);scene.advance(r::shot);fade_out(scene);
        require(read(store.path()).size()==1962 && read(store.path()).back()==0x7f,
                "save lost trailing score bytes");++cases;
    }
    // Real filesystem failure must propagate before the scene returns, while
    // the committed score remains available. No fresh OP is entered.
    {
        const auto directory=root/"write-failure";sf::HostStore store(directory);rng::Lcg32 random;
        r::Run run;run.digits[6]=1;
        r::Scene scene(assets,run,store.file(),[&] {return random.next15();},0,
            [&](const auto& op){store.apply(op);});
        fade_in(scene);
        const auto committed=read(store.path());fs::rename(store.path(),directory/"previous");
        fs::create_directory(store.path());bool rejected=false;
        try {press(scene,r::cancel);}catch(const std::exception&) {rejected=true;}
        require(rejected && !scene.finished() && read(directory/"previous")==committed,
                "failed host replacement lost committed score or completed scene");++cases;
    }
    std::cout<<"Registration scene/save/restart controls PASS cases="<<cases<<" muted=1\n";
}
}
int main(int argc,char** argv) {
    try {
        auto assets=synthetic();
        if(argc==2 && std::string(argv[1])=="--fade-clock") {
            sf::File file;rng::Lcg32 random;r::Run run;run.digits[6]=1;
            r::Scene scene(assets,run,file,[&] {return random.next15();});
            for(unsigned tick=1;tick<=35;++tick) {
                scene.advance(0);std::cout<<"IN "<<tick<<' '<<scene.tone()<<'\n';
            }
            scene.advance(r::cancel);
            require(scene.status()==r::Status::fade_out,"clock fixture did not save");
            for(unsigned tick=1;tick<=18;++tick) {
                scene.advance(0);std::cout<<"OUT "<<tick<<' '<<scene.tone()<<'\n';
            }
            require(scene.finished(),"clock fixture did not finish");
            return 0;
        }
        if(argc==5 && std::string(argv[1])=="--assets") {
            const fs::path directory(argv[2]);
            assets.graphics.pictures["HI01.PI"]=decode_pi(read(directory/"HI01.PI"));
            assets.numerals=read(directory/"SCNUM2.BFT");
            assets.graphics.gaiji=read(directory/"GAMEFT.BFT");
            assets.graphics.font_bitmap=read(argv[3]);
            std::string text(argv[4]);require(text.size()%2==0,"odd message hex");
            assets.non_turbo_message.clear();
            for(std::size_t i=0;i<text.size();i+=2)
                assets.non_turbo_message+=char(std::stoul(text.substr(i,2),nullptr,16));
        } else require(argc==1,"usage: [--fade-clock | --assets DIRECTORY FONT_BMP MESSAGE_HEX]");
        const auto root=fs::temp_directory_path()/("th04-registration-"+std::to_string(
            std::chrono::steady_clock::now().time_since_epoch().count()));
        require(fs::create_directory(root),"cannot reserve contract output");
        try {contracts(assets,root);}catch(...) {std::error_code ignored;fs::remove_all(root,ignored);throw;}
        fs::remove_all(root);
        return 0;
    }catch(const std::exception& e){std::cerr<<"ERROR: "<<e.what()<<'\n';return 1;}
}

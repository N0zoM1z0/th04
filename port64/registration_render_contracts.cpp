#include "registration_render.hpp"
#include "pi_image.hpp"
#include <fstream>
#include <sstream>
#include <stdexcept>

namespace reg=th04::portable::registration;
namespace sf=th04::portable::score_file;
namespace {
void require(bool b,const char* text) {if(!b)throw std::runtime_error(text);}
sf::Bytes read(const char* path) {
    std::ifstream file(path,std::ios::binary);require(bool(file),"registration asset missing");
    return sf::Bytes(std::istreambuf_iterator<char>(file),{});
}
sf::Bytes unhex(const std::string& s) {
    sf::Bytes result;if(s=="-")return result;
    require(s.size()%2==0,"invalid registration render hex");
    for(std::size_t i=0;i<s.size();i+=2)result.push_back(sf::Byte(std::stoul(s.substr(i,2),nullptr,16)));
    return result;
}
void write(std::ofstream& out,const sf::Bytes& bytes) {out.write(reinterpret_cast<const char*>(bytes.data()),std::streamsize(bytes.size()));require(bool(out),"registration capture write failed");}
}
// File-based binary output avoids Windows console/newline transformations.
// CASE starts a fresh graphics owner; SNAP retains pages, palette, TRAM and
// the composited frame. Commands can reproduce multiple edits on one page.
bool registration_render_cli(int argc,char** argv) {
    if(argc<2 || std::string(argv[1])!="--render")return false;
    require(argc==9,"usage: --render FIXTURES HI01.PI SCNUM2.BFT GAMEFT.BFT FONT.BMP MESSAGE_HEX OUTPUT");
    reg::GraphicsAssets assets;
    assets.graphics.pictures.emplace("HI01.PI",decode_pi(read(argv[3])));
    assets.numerals=read(argv[4]);assets.graphics.gaiji=read(argv[5]);assets.graphics.font_bitmap=read(argv[6]);
    const auto message=unhex(argv[7]);assets.non_turbo_message=std::string(message.begin(),message.end());
    std::ifstream input(argv[2]);require(bool(input),"registration render fixtures missing");
    std::ofstream out(argv[8],std::ios::binary);require(bool(out),"registration render output missing");
    std::unique_ptr<reg::Renderer> renderer;std::string line;
    while(std::getline(input,line)) {
        if(line.empty())continue;
        std::istringstream fields(line);std::string command;fields>>command;
        if(command=="CASE") {
            unsigned character,place;fields>>character>>place>>assets.text_weight;require(bool(fields),"invalid CASE");
            std::array<sf::Bytes,2> pages{sf::Bytes(640*400,3),sf::Bytes(640*400,9)};
            renderer=std::make_unique<reg::Renderer>(assets,sf::Byte(character),sf::Byte(place),std::move(pages),1);
            renderer->apply({reg::Kind::access,1});reg::Event load{reg::Kind::pi_load};load.text="HI01.PI";renderer->apply(load);
            renderer->apply({reg::Kind::pi_palette});renderer->apply({reg::Kind::pi_put});renderer->apply({reg::Kind::pi_free});
            renderer->apply({reg::Kind::copy,0});renderer->apply({reg::Kind::bfnt});continue;
        }
        require(bool(renderer),"render command precedes CASE");
        if(command=="SNAP") {
            int tone;fields>>tone;require(bool(fields),"invalid SNAP tone");
            write(out,renderer->canvas().page(0));write(out,renderer->canvas().page(1));
            write(out,sf::Bytes(renderer->canvas().palette().begin(),renderer->canvas().palette().end()));
            write(out,renderer->text_plane().bytes());write(out,renderer->rgb(0,tone));
        }else if(command=="table" || command=="name") {
            reg::Event e{command=="table" ? reg::Kind::table : reg::Kind::name};std::string hex;
            if(command=="table")fields>>e.a>>hex;else fields>>e.a>>e.b>>e.c>>hex;
            require(bool(fields),"invalid registration row fixture");e.bytes=unhex(hex);renderer->apply(e);
        }else if(command=="gaiji") {
            reg::Event e{reg::Kind::gaiji};fields>>e.a>>e.b>>e.c>>e.d;require(bool(fields),"invalid TRAM fixture");renderer->apply(e);
        }else if(command=="text") {
            reg::Event e{reg::Kind::text};fields>>e.a>>e.b>>e.c;require(bool(fields),"invalid text fixture");renderer->apply(e);
        }else if(command=="sprite") {
            int x,y;unsigned pattern;fields>>x>>y>>pattern;require(bool(fields),"invalid numeral fixture");renderer->put_numeral(x,y,pattern);
        }else if(command=="rect") {
            int x,y;unsigned w,h;fields>>x>>y>>w>>h;require(bool(fields),"invalid background fixture");renderer->restore_name_background(x,y,w,h);
        }else if(command=="clear_text")renderer->apply({reg::Kind::clear_text});
        else throw std::runtime_error("unknown registration render command");
    }
    return true;
}

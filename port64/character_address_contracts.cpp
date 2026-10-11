#include "registration_render.hpp"
#include <fstream>
#include <iostream>
#include <stdexcept>
#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif

namespace reg=th04::portable::registration;
using Bytes=th04::portable::score_file::Bytes;
namespace {
Bytes seed(std::size_t length) {
    Bytes result(length);
    for(std::size_t i=0;i<length;++i)result[i]=std::uint8_t(i);
    return result;
}
Bytes visible_seed() {
    auto result=seed(8000);
    for(unsigned i=0;i<4000;++i)result[i+4000]=result[i];
    return result;
}
std::string unhex(const std::string& text) {
    if(text=="-")return {};
    if(text.size()%2)throw std::invalid_argument("odd character vector hex");
    std::string result;
    for(std::size_t i=0;i<text.size();i+=2) {
        std::size_t count=0;const auto value=std::stoul(text.substr(i,2),&count,16);
        if(count!=2 || value>255)throw std::invalid_argument("invalid character vector hex");
        result+=char(value);
    }
    return result;
}
void require(bool condition,const char* message) {
    if(!condition)throw std::runtime_error(message);
}
void write(const Bytes& data) {
    std::cout.write(reinterpret_cast<const char*>(data.data()),std::streamsize(data.size()));
}
}

int main(int argc,char** argv) {
    try {
        if(argc==2 && std::string(argv[1])=="--pairs") {
#ifdef _WIN32
            _setmode(_fileno(stdout),_O_BINARY);
#endif
            const auto initial=visible_seed();
            for(unsigned mode=0;mode<2;++mode)for(unsigned value=0;value<65536;++value) {
                reg::TextPlane plane(initial);const auto attribute=std::uint16_t((value*257u)^0xe1u);
                if(!mode)plane.put_character(20,10,std::uint16_t(value),attribute);
                else plane.put_sjis(20,10,std::string{char(value>>8),char(value)},attribute);
                write(plane.bytes());
            }
            require(bool(std::cout),"character pair stream failed");return 0;
        }
        if(argc==3 && std::string(argv[1])=="--vectors") {
#ifdef _WIN32
            _setmode(_fileno(stdout),_O_BINARY);
#endif
            std::ifstream input(argv[2]);require(bool(input),"character vector file missing");
            const auto initial=seed(0x60000);std::string mode,value;int x,y;unsigned attribute,segment;
            while(input>>mode) {
                require(bool(input>>x>>y>>value>>attribute>>segment),"character vector fields");
                require(attribute<=65535 && segment<=65535,"character vector WORD overflow");
                reg::TextPlane plane;plane.load_memory(0x80000,initial);plane.set_segment(std::uint16_t(segment));
                if(mode=="putca") {
                    std::size_t count=0;const auto character=std::stoul(value,&count);
                    require(count==value.size() && character<=65535,"character vector WORD");
                    plane.put_character(x,y,std::uint16_t(character),std::uint16_t(attribute));
                }else if(mode=="putsa")plane.put_sjis(x,y,unhex(value),std::uint16_t(attribute));
                else throw std::invalid_argument("character vector mode");
                write(plane.physical_bytes(0x80000,0x60000));write(plane.bytes());
            }
            require(input.eof() && bool(std::cout),"character vector stream failed");return 0;
        }
        require(argc==1,"character address contracts CLI");
        reg::TextPlane edge,row;edge.put_character(80,0,0xa5,0xe1);row.put_character(0,1,0xa5,0xe1);
        require(edge.bytes()==row.bytes(),"ANK right-edge addressing");
        reg::TextPlane word,string;
        word.put_character(20,10,0x82a0,0xe1);string.put_sjis(20,10,std::string{char(0x82),char(0xa0)},0xe1);
        require(word.bytes()==string.bytes(),"standard Shift-JIS entry agreement");
        reg::TextPlane nul,empty;
        nul.put_sjis(0,0,std::string{char(0),char(0x81),char(0x40)},0xffff);
        require(nul.bytes()==empty.bytes(),"character string NUL entry");
        reg::TextPlane long_string;
        long_string.put_sjis(0,0,std::string(4097,'A'),0xe1);
        require(long_string.physical_bytes(0xa2000,4)==Bytes({0xe1,0,0xe1,0}),"ANK glyph/attribute alias order");
        reg::TextPlane last;last.put_character(79,24,0x82a0,0xffff);
        require(last.physical_bytes(0xa0f9e,4)==Bytes({4,0x22,0x84,0x22}),"last-row Kanji spill");
        std::cout<<"character address contracts PASS\n";return 0;
    }catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}

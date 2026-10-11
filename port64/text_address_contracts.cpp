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
constexpr unsigned start=0x80000,length=0x60000;
Bytes seed() {
    Bytes result(length);
    for(unsigned i=0;i<length;++i)result[i]=std::uint8_t(i);
    return result;
}
std::string unhex(const std::string& text) {
    if(text=="-")return {};
    if(text.size()%2)throw std::invalid_argument("odd text vector hex");
    std::string result;
    for(std::size_t i=0;i<text.size();i+=2) {
        std::size_t count=0;const auto value=std::stoul(text.substr(i,2),&count,16);
        if(count!=2 || value>255)throw std::invalid_argument("invalid text vector hex");
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
        if(argc==3 && std::string(argv[1])=="--vectors") {
#ifdef _WIN32
            _setmode(_fileno(stdout),_O_BINARY);
#endif
            std::ifstream input(argv[2]);require(bool(input),"text vector file missing");
            const auto initial=seed();std::string mode,value;int x,y;unsigned attribute,segment;
            while(input>>mode) {
                require(bool(input>>x>>y>>value>>attribute>>segment),"text vector fields");
                require(attribute<=65535 && segment<=65535,"text vector WORD overflow");
                reg::TextPlane plane;plane.load_memory(start,initial);plane.set_segment(std::uint16_t(segment));
                if(mode=="putca") {
                    std::size_t count=0;const auto glyph=std::stoul(value,&count);
                    require(count==value.size() && glyph<=65535,"text vector glyph");
                    plane.put(x,y,std::uint8_t(glyph),std::uint16_t(attribute));
                }else if(mode=="putsa")plane.put_string(x,y,unhex(value),std::uint16_t(attribute));
                else throw std::invalid_argument("text vector mode");
                write(plane.physical_bytes(start,length));write(plane.bytes());
            }
            require(input.eof() && bool(std::cout),"text vector stream failed");return 0;
        }
        require(argc==1,"text address contracts CLI");
        reg::TextPlane edge,row,wrapped,zero;
        edge.put(80,0,1,0xe1);row.put(0,1,1,0xe1);
        require(edge.bytes()==row.bytes(),"text right-edge address");
        wrapped.put(32768,32768,0x80,0xffff);zero.put(0,0,0x80,0xffff);
        require(wrapped.bytes()==zero.bytes(),"text WORD coordinate wrap");
        reg::TextPlane spill;spill.put(79,24,1,0xe1);
        require(spill.physical_bytes(0xa0f9e,4)==Bytes({0x56,1,0x56,0x81}),"last-row glyph spill");
        reg::TextPlane alias;
        alias.put_string(0,0,std::string(2049,char(1)),0xe1);
        require(alias.physical_bytes(0xa2000,4)==Bytes({0xe1,0,0xe1,0}),"glyph/attribute alias order");
        reg::TextPlane empty;const auto before=empty.bytes();
        empty.put_string(65535,65535,std::string{char(0),char(1)},0xffff);
        require(empty.bytes()==before,"text NUL termination");
        reg::TextPlane copied=spill;
        require(copied.physical_bytes(0xa0f9e,4)==spill.physical_bytes(0xa0f9e,4),"text copy retains spill");
        const auto visible=spill.bytes();reg::TextPlane packed(visible);
        require(packed.bytes()==visible,"packed TRAM compatibility");
        std::cout<<"text address contracts PASS\n";return 0;
    }catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}
}

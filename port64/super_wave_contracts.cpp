#include "super_wave.hpp"
#include <cmath>
#include <fstream>
#include <iostream>
#include <iterator>
#include <stdexcept>
#include <string>
int main(int argc,char** argv) {
    try {
        if(argc==1) {
            for(unsigned angle=0;angle<256;++angle) {
                const auto quarter=angle%128<=64 ? angle%128 : 128-angle%128;
                const auto value=std::min(127,int(128*std::sin(double(quarter)*3.14159265358979323846/128)));
                const auto expected=angle<128 ? value : -value;
                if(th04::portable::wave::sine(std::uint8_t(angle))!=expected)throw std::runtime_error("wave sine generation differs");
            }
            std::cout<<"Wave contracts PASS\n";return 0;
        }
        if(argc==3 && std::string(argv[1])=="--reject-zero") {
            std::ifstream file(argv[2],std::ios::binary);if(!file)throw std::runtime_error("wave zero-length asset missing");
            const std::vector<std::uint8_t> bytes{std::istreambuf_iterator<char>(file),{}};
            const th04::portable::sprite::Sheet sheet(bytes);
            try {th04::portable::wave::raster(sheet,0,96,16,0,64,0,[](int,int,std::uint8_t){});}
            catch(const std::domain_error&) {std::cout<<"Wave zero-length rejection PASS\n";return 0;}
            throw std::runtime_error("wave zero length was accepted");
        }
        if(argc!=3 || std::string(argv[1])!="--pixel-vectors")throw std::invalid_argument("expected wave fixture path");
        std::ifstream input(argv[2]);if(!input)throw std::runtime_error("cannot read wave fixtures");
        std::string name;unsigned image,amp,phase,seed;int left,top,length;
        while(input>>name>>image>>left>>top>>length>>amp>>phase>>seed) {
            std::ifstream file(name,std::ios::binary);if(!file)throw std::runtime_error("cannot read wave asset");
            const std::vector<std::uint8_t> bytes{std::istreambuf_iterator<char>(file),{}};
            const th04::portable::sprite::Sheet sheet(bytes);std::vector<std::uint8_t> screen(640*400);
            for(unsigned i=0;i<screen.size();++i)screen[i]=std::uint8_t((i*73+seed)&15);
            th04::portable::wave::raster(sheet,image,std::int16_t(left),std::int16_t(top),std::int16_t(length),
                std::uint16_t(amp),std::uint16_t(phase),[&](int x,int y,std::uint8_t color){screen.at(unsigned(y)*640+unsigned(x))=color;});
            std::cout.write(reinterpret_cast<const char*>(screen.data()),std::streamsize(screen.size()));
        }
        if(!input.eof())throw std::runtime_error("short wave fixture");
        return 0;
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}

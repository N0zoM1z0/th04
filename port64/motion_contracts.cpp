#include "motion.hpp"
#include <iostream>
#include <stdexcept>
#include <string>

namespace m = th04::portable::motion;
int main(int argc,char** argv) {
    try {
        if(argc==2 && std::string(argv[1])=="--angle-vectors") {
            int x,y,fx,fy;
            while(std::cin>>fx) {
                if(!(std::cin>>fy>>x>>y))throw std::invalid_argument("incomplete motion vector");
                for(auto value:{fx,fy,x,y})if(value<-32768 || value>32767)
                    throw std::invalid_argument("motion vector width");
                try {
                    std::cout<<unsigned(m::angle_to({m::Subpixel(fx),m::Subpixel(fy)},
                                                   {m::Subpixel(x),m::Subpixel(y)}))<<'\n';
                } catch(const std::domain_error&) {std::cout<<"divide-error\n";}
            }
            if(!std::cin.eof())throw std::invalid_argument("incomplete motion vector");
            return 0;
        }
        if(argc!=1)throw std::invalid_argument("motion contracts CLI");
        // Equal 0x8000 magnitudes bypass DIV. Unequal magnitudes select the
        // unusual branch, then truncate the successful quotient for XLAT.
        if(m::angle_to({}, {-32768,-32768})!=160 ||
           m::angle_to({}, {-32768,256})!=64 ||
           m::angle_to({}, {256,-32768})!=0 ||
           m::angle_to({32767,0},{-1,256})!=64)
            throw std::runtime_error("IATAN2 signed magnitude/XLAT/wrapped displacement");
        for(const auto point:{m::Point{-32768,0},m::Point{-32768,128},
                              m::Point{0,-32768},m::Point{128,-32768}}) {
            bool fault=false;
            try {(void)m::angle_to({},point);}catch(const std::domain_error&){fault=true;}
            if(!fault)throw std::runtime_error("IATAN2 DIV fault lost");
        }
        std::cout<<"motion contracts PASS\n";
        return 0;
    }catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}
}

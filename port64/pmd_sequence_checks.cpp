#include "pmd_sequence.hpp"
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>

using namespace th04::portable::pmd;
namespace {
void require(bool value,const char* message) {if(!value)throw std::runtime_error(message);}
Bytes read(const std::string& name) {
    std::ifstream file(name,std::ios::binary);require(bool(file),"cannot read PMD music");
    return {std::istreambuf_iterator<char>(file),{}};
}
void record(std::ostream& out,const Sequence& player,bool sharing=false) {
    const auto& s=player.state();
    out<<s.measure<<' '<<unsigned(s.fade)<<' '<<player.status()<<' '
       <<unsigned(s.timer_b)<<' '<<unsigned(s.bar_tick)<<' '<<unsigned(s.bar_length)<<' '<<unsigned(s.tempo);
    // Preserve the original eleven-track trace; FM3 has its own extended trace.
    for(unsigned n=0;n<11;++n){const auto& p=s.parts[n];out<<' '<<p.position<<' '<<p.loop<<' '<<unsigned(p.length)<<' '
        <<unsigned(p.loop_status)<<' '<<unsigned(p.notes)<<' '<<unsigned(p.volume)<<' '
        <<unsigned(p.transpose)<<' '<<unsigned(p.master_transpose)<<' '<<p.detune<<' '
        <<unsigned(p.instrument)<<' '<<unsigned(p.mask);}
    if(sharing) {
        const auto& e=player.ssg_effects().state();
        out<<' '<<e.resource<<' '<<e.next_frame<<' '<<e.tone<<' '<<e.tone_step<<' '
           <<unsigned(e.ticks)<<' '<<unsigned(e.noise)<<' '<<int(e.noise_step)<<' '
           <<unsigned(e.noise_interval)<<' '<<unsigned(e.noise_counter)<<' '
           <<unsigned(e.priority)<<' '<<unsigned(e.effect);
    }
    out<<'\n';
}
void contracts() {
    require(transpose_note(0,2,253)==255,"lowest C negative transposition must become a rest");
    require(transpose_note(15,127,0)==15,"canonical rest bypasses transposition");
    require(transpose_note(64,127,129)==64,"part/master transpose byte sum");
    // A synthetic three-tick phrase sets bar length, tempo and a real loop.
    // It verifies bounded self-modifying loop storage and musical durations.
    Bytes data(40,0x80);data[0]=0;
    for(unsigned p=0;p<13;++p){data[1+p*2]=35;data[2+p*2]=0;}
    const Bytes phrase{0xdf,3,0xfc,134,0xf6,0x40,2,0x4f,1,0x80};
    data[1]=26;data.resize(27);data.insert(data.end(),phrase.begin(),phrase.end());
    Sequence p;p.load(data);p.start();
    p.interrupt(2);require(p.state().measure==0 && p.state().timer_b==134,"phrase tempo");
    p.interrupt(1);require(p.state().measure==0,"Timer A cannot advance measures");
    p.interrupt(2);p.interrupt(2);require(p.state().measure==1,"phrase bar length");
    p.interrupt(2);require(p.state().parts[0].notes==3,"part loop replays note");
    p.fade(4);for(unsigned n=0;n<8;++n)p.interrupt(1);
    require(p.state().fade==4 && p.state().measure==1,"Timer A fade independence");
    p.stop();const auto measure=p.state().measure;
    for(unsigned n=0;n<256;++n)p.interrupt(3);
    require(p.state().measure==measure && p.state().fade==255,"stopped song freezes");
    p.start();require(p.state().measure==0 && p.state().fade==0,"restart resets music state");
    // Invalid resource admission must retain the previous owned bytes.
    const auto previous=p.music();bool rejected=false;
    try{p.load(Bytes{0,26,0});}catch(const std::exception&){rejected=true;}
    require(rejected && p.music()==previous,"invalid load destroys music");
    data[27]=0x81;p.load(data);p.start();rejected=false;
    try{p.interrupt(2);}catch(const std::invalid_argument&){rejected=true;}
    require(rejected,"unknown PMD command accepted");
    std::cout<<"PMD bytecode ownership, note/bar loops, Timer A fade and stopped/restart contracts PASS\n";
}
}
int main(int argc,char** argv) {
    try {
        if(argc==1){contracts();return 0;}
        if(argc==3 && std::string(argv[1])=="--transpose-bytes") {
            std::ofstream output(argv[2],std::ios::binary);require(bool(output),"transpose output");
            for(unsigned note=0;note<256;++note)for(unsigned sum=0;sum<256;++sum)
                output.put(char(transpose_note(std::uint8_t(note),0,std::uint8_t(sum))));
            for(unsigned part:{17u,128u,255u})
                for(unsigned note:{0u,11u,12u,13u,14u,15u,16u,31u,63u,112u,123u,127u,128u,255u})
                    for(unsigned sum=0;sum<256;++sum)
                        output.put(char(transpose_note(std::uint8_t(note),std::uint8_t(part),std::uint8_t(sum-part))));
            output.close();require(bool(output),"transpose write failed");return 0;
        }
        require(argc==5 || argc==6,"PMD trace: song board operation-file output-file [ssg]");
        const bool sharing=argc==6;require(!sharing || std::string(argv[5])=="ssg","PMD extended trace mode");
        const int board=std::stoi(argv[2]);require(board>=0 && board<=2,"invalid PMD board");
        Sequence player(board==0 ? Board::fm26 : board==2 ? Board::fm86 : Board::speakboard);
        player.load(read(argv[1]));player.start();
        std::ifstream operations(argv[3]);require(bool(operations),"cannot read PMD operations");
        std::ofstream output(argv[4]);require(bool(output),"cannot write PMD trace");
        record(output,player,sharing);char op;int value;
        while(operations>>op>>value) {
            if(op=='I') {require(value>=0 && value<=3,"invalid PMD timer status");player.interrupt(std::uint8_t(value));}
            else if(op=='F') {require(value>=-128 && value<=127,"invalid fade speed");player.fade(std::int8_t(value));}
            else if(op=='S')player.stop();
            else if(op=='R')player.start();
            else throw std::invalid_argument("unknown PMD trace operation");
            record(output,player,sharing);
        }
        require(operations.eof(),"invalid PMD operation file");output.close();require(bool(output),"PMD trace write failed");
        return 0;
    }catch(const std::exception& e){std::cerr<<"PMD: "<<e.what()<<'\n';return 1;}
}

#include "hud_popup.hpp"
#include "score.hpp"
#include <iostream>
#include <iomanip>
#include <string>
using namespace th04::portable;
int main(int argc,char** argv) {
    if(argc==1) {
        popup::Snapshot s;registration::TextPlane text;popup::request(s,popup::Kind::full_power);
        for(unsigned i=0;i<128;++i)popup::update(s,text);
        if(s.frame!=128 || !s.active || !s.reached || s.left!=20)return 1;
        popup::update(s,text);if(s.active || s.frame)return 1;
        s={};text={};score::Snapshot board;board.delta=10000;board.hiscore.fill(9);
        popup::request(s,popup::Kind::bonus,25000);popup::update(s,text);
        board.popup_id=s.requested;board.popup_callback=s.active;score::update(board);
        if(board.popup_callback)popup::request(s,popup::Kind(board.popup_id));
        if(s.bonus!=25000 || s.frame!=1)return 1;
        std::cout<<"MAIN popup lifecycle/score-tail contracts: PASS\n";return 0;
    }
    if(argc!=2 || std::string(argv[1])!="--vectors")return 2;
    popup::Snapshot s;registration::TextPlane text;score::Snapshot board;std::string op;unsigned id,bonus;
    while(std::cin>>op) {
        if(op=="S") {std::cin>>id>>bonus;s={};text={};board={};board.delta=10000;board.hiscore.fill(9);popup::request(s,popup::Kind(id),bonus);}
        else if(op=="Q") {std::cin>>id>>bonus;popup::request(s,popup::Kind(id),bonus);}
        else if(op!="U" && op!="R")return 2;
        if(op=="R") {
            board.popup_id=s.requested;board.popup_callback=s.active;
            for(const auto& event:score::update(board))if(event.kind==score::Kind::gaiji)
                text.put_string(int(event.left),int(event.row),event.bytes,std::uint16_t(event.value));
            if(board.popup_callback)popup::request(s,popup::Kind(board.popup_id));
        } else popup::update(s,text);
        std::cout<<+s.frame<<' '<<s.length<<' '<<+s.current<<' '<<s.reached<<' '<<s.left<<' '<<s.destination<<' '<<+s.requested<<' '<<(s.active ? 0x67e8 : 0x11be)<<' '<<s.bonus<<' ';
        for(auto b:s.shift)std::cout<<std::hex<<std::setfill('0')<<std::setw(2)<<+b;
        std::cout<<' ';for(auto b:text.physical_bytes(0xa0000,0x4000))std::cout<<std::hex<<std::setfill('0')<<std::setw(2)<<+b;
        std::cout<<std::dec<<'\n';
    }
}

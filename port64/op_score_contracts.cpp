#include "op_score.hpp"
#include "random_lcg.hpp"
#include <algorithm>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
using namespace th04::portable;
namespace sf=score_file;
namespace {
sf::Bytes unhex(const std::string& s) {
    if(s=="-")return {};
    if(s.size()%2)throw std::invalid_argument("odd hex fixture");
    sf::Bytes b;
    for(unsigned i=0;i<s.size();i+=2)b.push_back(sf::Byte(std::stoul(s.substr(i,2),nullptr,16)));
    return b;
}
template<class T> void hex(const T& data) {
    constexpr char a[]="0123456789abcdef";if(data.empty())std::cout<<'-';
    for(auto v:data)std::cout<<a[v>>4]<<a[v&15];
}
void require(bool value,const char* s) {if(!value)throw std::runtime_error(s);}
void trace(const char* path) {
    std::ifstream file(path);require(bool(file),"OP fixtures missing");
    unsigned op,rank,configured,extra,present,stage;std::uint32_t seed;
    std::string first,second,cleared,bytes,actions;unsigned index=0;
    while(file>>op>>seed>>rank>>configured>>extra>>present>>stage>>first>>second>>cleared>>bytes>>actions) {
        op_score::Snapshot initial;auto x=unhex(first),y=unhex(second),flags=unhex(cleared);
        require(x.size()==196 && y.size()==196 && flags.size()==10,"OP fixture shape");
        std::copy(x.begin(),x.end(),initial.first.begin());std::copy(y.begin(),y.end(),initial.second.begin());
        for(unsigned c=0;c<2;++c)for(unsigned r=0;r<5;++r)initial.cleared[c][r]=flags[c*5+r];
        initial.rank=sf::Byte(rank);initial.extra_unlocked=sf::Byte(extra);
        op_score::State state(initial);sf::File score(present,unhex(bytes));rng::Lcg32 random(seed);unsigned draws=0;
        const auto next=[&]{++draws;return random.next15();};int result=-1,character=-1,shot=-1;
        if(op==0) {result=op_score::decode_both(initial.first,initial.second);state=op_score::State(initial);}
        else if(op==1)result=state.load_both(score,next);
        else if(op==2)state.recreate(score,next);
        else if(op==3)state.read(score,sf::Byte(configured),next);
        else if(op!=4)throw std::invalid_argument("OP operation");
        if(op==4) {
            selection::State menu(state.availability(stage==6));
            for(auto key:unhex(actions)) {
                const auto answer=menu.handle(menu::Input(key));
                if(answer.kind!=selection::ResultKind::none) {
                    result=answer.kind==selection::ResultKind::canceled ? 1 : 0;
                    character=int(answer.playchar);shot=int(answer.shot_type);break;
                }
            }
            require(result>=0,"selection fixture omitted return");
        }
        std::cout<<"CASE "<<index++<<'\n';
        constexpr const char* names[]{"exists","open","seek","read","write","close"};
        for(const auto& e:score.operations()) {std::cout<<names[unsigned(e.kind)]<<' '<<e.a<<' '<<e.b<<' ';hex(e.data);std::cout<<'\n';}
        const auto& s=state.snapshot();std::cout<<"END "<<result<<' '<<random.state()<<' '<<draws<<' '<<int(score.present())<<' '<<+s.rank<<' '<<+s.extra_unlocked<<' '<<character<<' '<<shot<<' ';
        hex(s.first);std::cout<<' ';hex(s.second);std::cout<<' ';
        for(const auto& c:s.cleared)hex(c);
        std::cout<<' ';hex(score.bytes());std::cout<<'\n';
    }
    require(file.eof(),"short OP fixture");
}
void contracts() {
    op_score::Snapshot s;sf::initialize_rows(s.first);sf::initialize_rows(s.second);rng::Lcg32 random;
    auto encode=[&](sf::Section& section){sf::encode(section,[&]{return random.next15();});};
    encode(s.first);encode(s.second);auto changed=s;changed.first[3]^=0x80;
    const auto untouched=changed.second;require(op_score::decode_both(changed.first,changed.second)==1 && changed.second==untouched,"OP first WORD checksum failed to preserve second");
    changed=s;changed.second[3]^=0x80;require(!op_score::decode_both(changed.first,changed.second),"OP second checksum high byte became strict");
    s.cleared[0][0]=3;s.cleared[1][4]=3;op_score::State state(s);
    auto available=state.availability(true);require(!available[0][0] && !available[1][1],"Extra selection included Easy/Extra rank");
    selection::State none(available);none.handle(menu::Input::confirm);auto answer=none.handle(menu::Input::confirm);
    require(answer.kind==selection::ResultKind::chosen && answer.playchar==application::Playchar::marisa && answer.shot_type==application::ShotType::b,"Original empty-mask Marisa/B fallback changed");
    sf::File missing;state.read(missing,3,[&]{return random.next15();});require(state.snapshot().rank==3 && missing.bytes().size()==1960,"OP missing file did not recreate/restore rank");
    std::cout<<"OP score reader/strict-first-checksum/Extra selection contracts PASS\n";
}
}
int main(int argc,char** argv) {try {if(argc==3 && std::string(argv[1])=="--trace")trace(argv[2]);else if(argc==1)contracts();else throw std::invalid_argument("OP score arguments");return 0;}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}

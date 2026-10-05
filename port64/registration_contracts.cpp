#include "registration.hpp"
#include "random_lcg.hpp"
#include <algorithm>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
namespace reg=th04::portable::registration;
namespace sf=th04::portable::score_file;
namespace rng=th04::portable::rng;
namespace {
void require(bool b,const char* message) { if(!b)throw std::runtime_error(message); }
sf::Bytes unhex(const std::string& text) {
    if(text=="-")return {};
    require(text.size()%2==0,"odd fixture hex size");sf::Bytes bytes;
    for(std::size_t i=0;i<text.size();i+=2)bytes.push_back(sf::Byte(std::stoul(text.substr(i,2),nullptr,16)));
    return bytes;
}
void hex(const sf::Bytes& bytes) {
    static constexpr char digits[]="0123456789abcdef";
    if(bytes.empty()){std::cout<<'-';return;}
    for(auto b:bytes)std::cout<<digits[b>>4]<<digits[b&15];
}
void event(const reg::Event& e) {
    const auto n=[&](const char* name) {std::cout<<name<<' '<<e.a<<' '<<e.b<<' '<<e.c<<' '<<e.d<<' ';hex(e.bytes);std::cout<<' '<<(e.text.empty()?"-":e.text)<<'\n';};
    if(e.kind==reg::Kind::file) {
        static const char* names[]={"exists","open","seek","read","write","close"};
        std::cout<<names[unsigned(e.io.kind)]<<' '<<e.io.a<<' '<<e.io.b<<' ';hex(e.io.data);std::cout<<'\n';return;
    }
    static const char* names[]={"tone","access","pi_load","pi_palette","pi_put","pi_free","copy","bfnt","file","table","text","sound","song","fade","gaiji","name","wait","free_sprites","clear_text"};
    n(names[unsigned(e.kind)]);
}
void trace(const char* path) {
    std::ifstream input(path);require(bool(input),"registration fixture missing");std::string line;unsigned index=0;
    while(std::getline(input,line)) {
        if(line.empty())continue;
        std::istringstream fields(line);std::uint32_t seed;unsigned stage,rank,character,shot,turbo,end,present,initial;
        std::string digit_text,file_text,key_text;fields>>seed>>stage>>rank>>character>>shot>>turbo>>end>>present>>initial>>digit_text>>file_text>>key_text;
        require(bool(fields),"invalid registration fixture");auto digits=unhex(digit_text);require(digits.size()==8,"invalid score digits");
        reg::Run run{sf::Byte(stage),sf::Byte(rank),sf::Byte(character),sf::Byte(shot),sf::Byte(turbo),sf::Byte(end)};
        std::copy(digits.begin(),digits.end(),run.digits.begin());sf::File file(present!=0,unhex(file_text));
        rng::Lcg32 random(seed);unsigned draws=0;reg::Menu menu(run,file,[&] {++draws;return random.next15();},std::uint16_t(initial));
        std::cout<<"CASE "<<index++<<'\n';std::size_t at=0;
        const auto flush=[&] {while(at<menu.events().size())event(menu.events()[at++]);};flush();
        std::istringstream keys(key_text);std::string key;
        while(!menu.finished() && std::getline(keys,key,',')) {
            menu.advance(std::uint16_t(std::stoul(key)));flush();
            if(!menu.finished()) {
                std::cout<<"FRAME "<<menu.ticks()-1<<' '<<menu.name_cursor()<<' '<<menu.alphabet_column()<<' '
                    <<menu.alphabet_row()<<' '<<menu.input_lock()<<' '<<unsigned(menu.repeat_frames())<<' ';
                hex(sf::Bytes(menu.section().begin(),menu.section().end()));std::cout<<'\n';
            }
        }
        require(menu.finished(),"registration fixture did not confirm");
        std::cout<<"END "<<unsigned(menu.rank())<<' '<<unsigned(menu.character())<<' '<<unsigned(menu.place())<<' '
            <<menu.ticks()<<' '<<random.state()<<' '<<draws<<' '<<int(file.present())<<' ';
        hex(sf::Bytes(menu.section().begin(),menu.section().end()));std::cout<<' ';hex(file.bytes());std::cout<<'\n';
    }
}
void contracts() {
    // Missing-file setup and Esc confirmation save all sections but never
    // discard the new row. Verify behavior through a fresh decoded file load.
    sf::File file;rng::Lcg32 random(318);unsigned draws=0;const auto next=[&] {++draws;return random.next15();};
    reg::Run run;run.stage=5;run.end_sequence=0xff;run.digits[6]=1;
    reg::Menu menu(run,file,next);
    require(menu.editable() && menu.place()==0 && draws==20,"registration setup differs");
    menu.advance(0);menu.advance(reg::shot);menu.advance(0);menu.advance(0);menu.advance(reg::cancel);
    require(menu.finished() && draws==42,"partial-name Escape did not save");
    sf::Section loaded{};sf::load_for(loaded,file,0,0,next);
    require(loaded[4]==0xaa && loaded[5]==0xc4 && loaded[174]==1,"saved name/clear bit differs");
    reg::Run normal;normal.turbo=0;normal.rank=1;normal.end_sequence=0xfe;
    reg::Menu no_entry(normal,file,next);
    require(!no_entry.editable() && no_entry.finished(),"non-Turbo path allowed name editing");
    auto wait=std::find_if(no_entry.events().begin(),no_entry.events().end(),[](const auto& e){return e.kind==reg::Kind::wait;});
    require(wait!=no_entry.events().end() && wait->a==0,"no-entry path omitted acknowledgement");
    std::cout<<"Registration ranking, partial name and acknowledgement controls PASS\n";
}
}
int main(int argc,char** argv) {
    try {
        if(argc==1)contracts();else if(argc==3 && std::string(argv[1])=="--trace")trace(argv[2]);
        else throw std::runtime_error("usage: th04-port64-registration-contracts [--trace FIXTURES]");
        return 0;
    }catch(const std::exception& e){std::cerr<<"ERROR: "<<e.what()<<'\n';return 1;}
}

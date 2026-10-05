#include "score_file.hpp"
#include "random_lcg.hpp"
#include <algorithm>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>

namespace sf=th04::portable::score_file;
namespace rng=th04::portable::rng;
namespace {
void require(bool b,const char* reason) {if(!b)throw std::runtime_error(reason);}
sf::Bytes unhex(const std::string& text) {
    if(text=="-")return {};
    if(text.size()%2)throw std::runtime_error("odd hex input");
    sf::Bytes b;
    for(std::size_t i=0;i<text.size();i+=2) {
        const auto part=text.substr(i,2);std::size_t end=0;const auto n=std::stoul(part,&end,16);
        if(end!=2 || n>255)throw std::runtime_error("invalid hex input");
        b.push_back(sf::Byte(n));
    }
    return b;
}
template<typename T> void hex(const T& bytes) {
    static constexpr char alphabet[]="0123456789abcdef";
    if(bytes.empty()) {std::cout<<'-';return;}
    for(auto b:bytes)std::cout<<alphabet[b>>4]<<alphabet[b&15];
}
void contracts() {
    sf::Section plain{};for(unsigned i=0;i<plain.size();++i)plain[i]=sf::Byte(i*73+19);
    rng::Lcg32 random(0x12345678);auto next=[&] {return random.next15();};
    auto encrypted=plain;sf::encode(encrypted,next);auto decoded=encrypted;
    require(!sf::decode(decoded),"valid encoded section rejected");
    require(std::equal(plain.begin()+4,plain.end(),decoded.begin()+4),"cipher chain roundtrip differs");
    auto high_checksum=encrypted;high_checksum[3]^=0x80;
    require(!sf::decode(high_checksum),"original ignores checksum high-byte corruption");
    auto low_checksum=encrypted;low_checksum[2]^=1;
    require(sf::decode(low_checksum)!=0,"low checksum corruption accepted");
    sf::File short_file(true,sf::Bytes(137,0x11));sf::Section short_buffer;short_buffer.fill(0xa5);
    short_file.open(sf::OpenMode::read);short_file.read(short_buffer);short_file.close();
    require(std::all_of(short_buffer.begin(),short_buffer.begin()+137,[](auto b){return b==0x11;}) &&
        std::all_of(short_buffer.begin()+137,short_buffer.end(),[](auto b){return b==0xa5;}),"short read cleared unread bytes");
    sf::File appended(true,sf::Bytes(2111,0x22));appended.open(sf::OpenMode::append);appended.write(plain);appended.close();
    require(appended.bytes().size()==2111+196 && std::equal(plain.begin(),plain.end(),appended.bytes().begin()+2111),
        "append open did not seek to end");
    auto work=plain;sf::initialize_rows(work);
    require(work[175]==plain[175] && std::equal(work.begin()+186,work.end(),plain.begin()+186),"initializer erased unused bytes");
    // Keep distinct row terminators to expose a whole-nine-byte name copy.
    for(unsigned row=0;row<10;++row)work[4+row*9+8]=sf::Byte(20+row);
    th04::portable::score::Digits digits{};digits[4]=9;
    require(sf::insert(work,digits,5,0xff)==1,"equal scores must insert before equal row");
    for(unsigned row=0;row<10;++row)require(work[4+row*9+8]==20+row,"insertion moved a name terminator");
    sf::File missing;work=plain;rng::Lcg32 start(1);unsigned draws=0;
    const auto callback=[&] {++draws;return start.next15();};
    require(sf::load_for(work,missing,1,3,callback),"missing file did not recreate");
    require(missing.bytes().size()==1960 && draws==20 && missing.changed(),"recreation did not write all ten sections");
    for(unsigned row=0;row<10;++row) {
        sf::Section section;std::copy_n(missing.bytes().begin()+row*196,196,section.begin());
        require(!sf::decode(section),"recreated checksum differs");
        require(section[175]==plain[175] && std::equal(section.begin()+186,section.end(),plain.begin()+186),"recreated reserved bytes differ");
    }
    sf::File loaded(true,missing.bytes());draws=0;
    require(!sf::load_for(work,loaded,1,3,callback) && !draws && !loaded.changed(),"valid load recreated/re-keyed file");
    work[4]=0xaa;sf::save(work,loaded,1,3,callback);
    require(draws==22 && loaded.bytes().size()==1960,"save did not re-key all ten sections");
    sf::Section last;std::copy_n(loaded.bytes().begin()+9*196,196,last.begin());
    require(work==last,"save retained selected decoded buffer instead of final encoded section9");
    std::cout<<"Score file cipher, ranking and full-file lifecycle controls PASS\n";
}
void trace(const char* fixtures) {
    std::ifstream input(fixtures);if(!input)throw std::runtime_error("score fixtures missing");
    unsigned index=0,operation,character,rank,stage,end,present;std::uint32_t seed;std::string section_text,file_text,digit_text;
    while(input>>operation>>seed>>character>>rank>>stage>>end>>present>>section_text>>file_text>>digit_text) {
        auto section_bytes=unhex(section_text);require(section_bytes.size()==196,"section size differs");
        sf::Section section;std::copy(section_bytes.begin(),section_bytes.end(),section.begin());
        auto d=unhex(digit_text);require(d.size()==8,"score digit size differs");th04::portable::score::Digits digits;
        std::copy(d.begin(),d.end(),digits.begin());sf::File file(present!=0,unhex(file_text));
        rng::Lcg32 random(seed);unsigned draws=0;const auto next=[&] {++draws;return random.next15();};
        int result=-1,place=0xa5;
        switch(operation) {
        case 0:sf::encode(section,next);break;
        case 1:result=sf::decode(section);break;
        case 2:sf::recreate(section,file,next);break;
        case 3:result=sf::load_for(section,file,sf::Byte(character),sf::Byte(rank),next);break;
        case 4:sf::save(section,file,sf::Byte(character),sf::Byte(rank),next);break;
        case 5:place=sf::insert(section,digits,sf::Byte(stage),sf::Byte(end));break;
        default:throw std::runtime_error("unknown score operation");
        }
        std::cout<<"CASE "<<index++<<'\n';
        for(const auto& e:file.operations()) {
            const char* names[]={"exists","open","seek","read","write","close"};
            std::cout<<names[unsigned(e.kind)]<<' '<<e.a<<' '<<e.b<<' ';hex(e.data);std::cout<<'\n';
        }
        std::cout<<"END "<<result<<' '<<place<<' '<<random.state()<<' '<<draws<<' '<<int(file.present())<<' ';
        hex(section);std::cout<<' ';hex(file.bytes());std::cout<<'\n';
    }
    if(!input.eof())throw std::runtime_error("invalid fixture input");
}
}
int main(int argc,char** argv) {
    try {
        if(argc==1)contracts();
        else if(argc==3 && std::string(argv[1])=="--trace")trace(argv[2]);
        else throw std::runtime_error("usage: th04-port64-score-file-contracts [--trace FIXTURES]");
        return 0;
    } catch(const std::exception& e) {std::cerr<<"ERROR: "<<e.what()<<'\n';return 1;}
}

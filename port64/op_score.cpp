#include "op_score.hpp"
#include <stdexcept>

namespace th04::portable::op_score {
namespace sf=score_file;
void State::browse_rank(sf::Byte rank) {
    if(rank>=5)throw std::out_of_range("OP ranking index");
    snapshot_.rank=rank;
}
sf::Byte decode_both(sf::Section& first,sf::Section& second) {
    sf::decode(first);
    unsigned sum=0;for(unsigned i=sf::names_offset;i<first.size();++i)sum+=first[i];
    const unsigned stored=unsigned(first[2])|(unsigned(first[3])<<8);
    if(stored!=sum)return 1;
    return sf::decode(second);
}
void State::recreate(sf::File& file,const sf::Random& next) {
    sf::initialize_rows(snapshot_.first);file.open(sf::OpenMode::create);
    for(unsigned i=0;i<sf::section_count;++i) {
        sf::encode(snapshot_.first,next);file.write(snapshot_.first);
        // Original recreation calls OP's two-column decoder even though it
        // only encoded/wrote first. Retain second's repeated transformations.
        decode_both(snapshot_.first,snapshot_.second);
    }
    file.close();
}
bool State::load_both(sf::File& file,const sf::Random& next) {
    if(file.exists()) {
        file.open(sf::OpenMode::read);file.seek(unsigned(snapshot_.rank)*sf::section_size,0);
        file.read(snapshot_.first);file.seek(4*sf::section_size,1);
        file.read(snapshot_.second);file.close();
        if(!decode_both(snapshot_.first,snapshot_.second))return false;
    }
    recreate(file,next);return true;
}
void State::read(sf::File& file,sf::Byte configured_rank,const sf::Random& next) {
    snapshot_.rank=0;
    while(snapshot_.rank<5) {
        if(load_both(file,next))break;
        for(unsigned character=0;character<2;++character) {
            auto& mask=snapshot_.cleared[character][snapshot_.rank];
            mask=(character ? snapshot_.second : snapshot_.first)[sf::cleared_offset];
            if(mask>3)mask=0;
        }
        if(snapshot_.rank) snapshot_.extra_unlocked|=snapshot_.cleared[0][snapshot_.rank]|snapshot_.cleared[1][snapshot_.rank];
        ++snapshot_.rank;
    }
    snapshot_.rank=configured_rank;
}
selection::Availability State::availability(bool extra) const {
    if(!extra)return selection::State::all_available();
    selection::Availability result{};
    for(unsigned character=0;character<2;++character)for(unsigned shot=0;shot<2;++shot)
        for(unsigned rank=1;rank<4;++rank)result[character][shot]=result[character][shot] || (snapshot_.cleared[character][rank]&(1u<<shot));
    return result;
}
}

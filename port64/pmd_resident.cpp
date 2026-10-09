#include "pmd_resident.hpp"
#include <stdexcept>

namespace th04::portable::sound {
ResidentPmd::ResidentPmd(PmdProfile profile):board_(profile.board),
    player_(profile.board,profile.master_hz,std::move(profile.rhythm_rom),
            [this](pmd::StereoSample value){samples_.push_back(value);}) {
    // Installation begins stopped (fade/loop FF), without elapsed time.
    // These release/key-off writes are repeated by the actual initialization;
    // both leave the reset chip silent. Restore the complete installed mirror.
    player_.stop_music();
    for(unsigned bank=0;bank<2;++bank)for(unsigned a=0;a<256;++a)
        player_.mirror(std::uint8_t(bank),std::uint8_t(a),0);
    install();
}
Drivers ResidentPmd::drivers() const {return {true,false,std::uint16_t(0x4800+unsigned(board_))};}
void ResidentPmd::write(unsigned bank,unsigned address,unsigned value) {
    const pmd::FmWrite w{std::uint8_t(bank),std::uint8_t(address),std::uint8_t(value)};
    installation_.push_back(w);player_.mirror(w.bank,w.address,w.value);player_.initialize(w);
}
void ResidentPmd::install() {
    // Board numbers preserve the original service replies: PMD=0, PMDB2=1,
    // PMD86=2. The legacy pmd::Board labels are not hardware identity names.
    if(board_==pmd::Board::fm86) {
        write(0,0x29,0x83);write(1,0,1);write(1,0x10,0x17);write(1,0x10,0x80);
        write(1,0,0x60);write(1,1,2);write(1,12,255);write(1,13,255);
        write(1,2,255);write(1,3,31);write(1,4,255);write(1,5,255);
        write(1,8,0);write(1,0x10,0);write(1,0x10,0x80);write(1,0,1);
    }
    write(0,7,63);write(0,0x29,0);
    for(unsigned a=0x24;a<=0x26;++a)write(0,a,0);
    write(0,0x27,63);write(0,0x29,0x83);write(0,6,0);
    const unsigned banks=board_==pmd::Board::fm26 ? 1 : 2;
    for(unsigned bank=0;bank<banks;++bank)for(unsigned channel=0;channel<3;++channel)
        write(bank,0xb4+channel,192);
    write(0,0x22,0);
    if(board_==pmd::Board::fm26) {write(1,0x10,0x80);write(1,0x10,0x18);}
    else {write(0,0x10,255);write(0,0x11,48);}
    write(0,7,191);
    for(unsigned bank=0;bank<banks;++bank)for(unsigned slot=0;slot<4;++slot)
        for(unsigned channel=0;channel<3;++channel)write(bank,0x80+slot*4+channel,255);
    for(unsigned bank=0;bank<banks;++bank)for(unsigned channel=0;channel<3;++channel)
        write(0,0x28,channel+(bank ? 4 : 0));
    write(0,7,191);
    if(board_==pmd::Board::speakboard) {write(1,0x10,0x80);write(1,0x10,0x18);}
    write(0,0x26,200);write(0,0x25,0);write(0,0x24,0);write(0,0x27,63);write(0,0x29,0x83);
}
std::uint16_t ResidentPmd::command(std::uint16_t ax) {
    const auto low=std::uint8_t(ax);const auto& sequence=player_.player().player().music().sequence();
    switch(ax>>8) {
    case 0:player_.start_music();break;
    case 1:player_.stop_music();break;
    case 2:player_.fade(std::int8_t(low<128 ? int(low) : int(low)-256));break;
    case 5:return sequence.state().measure;
    case 6:destination_=Buffer::music;break;
    case 8:return std::uint16_t((ax&0xff00)|sequence.state().fade);
    case 9:return drivers().type_reply;
    case 10:return sequence.status();
    case 11:destination_=Buffer::effects;break;
    case 12:player_.start_effect(low);break;
    default:throw std::invalid_argument("unrecovered resident PMD service");
    }
    return ax;
}
std::optional<int> ResidentPmd::consume(const Request& q,const Reader& reader) {
    switch(q.kind) {
    case Kind::interrupt:
        if(q.a!=0x60)return std::nullopt;
        return command(q.b);
    case Kind::open:
        if(open_ || !reader)throw std::logic_error("resident PMD file open");
        filename_=q.name;file_=reader(filename_);destination_=Buffer::none;open_=true;return 0;
    case Kind::read:
        if(!open_ || destination_==Buffer::none || q.a!=0x5000)
            throw std::logic_error("resident PMD buffer read order");
        // Failure/capacity handling is an explicit native resource boundary.
        // Do not publish stale data or invent musical progress after failure.
        try {
            if(!file_)throw std::runtime_error("missing PMD resource: "+filename_);
            if(destination_==Buffer::music)player_.load_music(*file_);else player_.load_effects(*file_);
            return int(file_->size());
        } catch(...) {
            file_.reset();filename_.clear();destination_=Buffer::none;open_=false;throw;
        }
    case Kind::close:
        if(!open_)throw std::logic_error("resident PMD file close");
        file_.reset();filename_.clear();destination_=Buffer::none;open_=false;return 0;
    default:return std::nullopt;
    }
}
std::vector<pmd::StereoSample> ResidentPmd::advance(std::uint64_t ns) {
    if(!samples_.empty())throw std::logic_error("resident PCM block not drained");
    player_.advance_ns(ns);auto result=std::move(samples_);samples_.clear();return result;
}
}

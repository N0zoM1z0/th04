#include "score_file.hpp"
#include <algorithm>
#include <stdexcept>

namespace th04::portable::score_file {
namespace {
constexpr Byte rotate_right3(Byte b) { return Byte((b>>3)|(b<<5)); }
std::uint16_t sum(const Section& section) {
    std::uint16_t total=0;
    for(std::size_t i=names_offset;i<section_size;++i)total=std::uint16_t(total+section[i]);
    return total;
}

}
bool File::exists() {
    operations_.push_back({IO::exists,int(exists_)});return exists_;
}
void File::open(OpenMode mode) {
    if(open_)throw std::logic_error("score file is already open");
    if(mode!=OpenMode::create && !exists_)throw std::runtime_error("score file is missing");
    if(mode==OpenMode::create) {bytes_.clear();exists_=true;changed_=true;}
    // file_append opens read/write and performs DOS seek-to-end.
    // Save then seeks explicitly, but the byte-store API retains that state.
    mode_=mode;open_=true;position_=mode==OpenMode::append ? bytes_.size() : 0;
    operations_.push_back({IO::open,int(mode)});
}
void File::seek(std::uint32_t offset,unsigned origin) {
    if(!open_ || origin>1)throw std::logic_error("invalid score seek");
    position_=(origin ? position_ : 0)+offset;
    operations_.push_back({IO::seek,int(offset),int(origin)});
}
void File::read(Section& section) {
    if(!open_)throw std::logic_error("score file is closed");
    const auto count=position_<bytes_.size() ? std::min(section_size,bytes_.size()-position_) : 0;
    Bytes data;
    if(count) {
        data.assign(bytes_.begin()+position_,bytes_.begin()+position_+count);
        std::copy(data.begin(),data.end(),section.begin());
    }
    // DOS file_read leaves the unread suffix of the shared HI buffer intact.
    // Load/save do not check AX's returned count before decoding that buffer.
    position_+=count;operations_.push_back({IO::read,int(section_size),int(count),std::move(data)});
}
void File::write(const Section& section) {
    if(!open_ || mode_==OpenMode::read)throw std::logic_error("score file is not writable");
    if(bytes_.size()<position_+section_size)bytes_.resize(position_+section_size);
    std::copy(section.begin(),section.end(),bytes_.begin()+position_);
    position_+=section_size;changed_=true;
    operations_.push_back({IO::write,int(section_size),int(section_size),Bytes(section.begin(),section.end())});
}
void File::close() {
    if(!open_)throw std::logic_error("score file is closed");
    open_=false;operations_.push_back({IO::close});
}
void encode(Section& section,const Random& next) {
    const auto checksum=sum(section);section[2]=Byte(checksum);section[3]=Byte(checksum>>8);
    section[0]=Byte(next());section[1]=Byte(next());
    Byte feedback=0;
    // Reverse traversal feeds the NEXT encoded byte into the current byte.
    // Signed original key promotion narrows to the same modulo-256 byte here.
    for(std::size_t i=section_size;i-->names_offset;) {
        section[i]=Byte(section[i]-section[0]-feedback);
        feedback=Byte(rotate_right3(section[i])^section[1]);
    }
}
Byte decode(Section& section) {
    // Ascending traversal must read i+1 while it is still encoded. Reversing
    // this loop or feeding the already decoded byte breaks the chain.
    for(std::size_t i=names_offset;i+1<section_size;++i)
        section[i]=Byte(section[i]+section[0]+(rotate_right3(section[i+1])^section[1]));
    section.back()=Byte(section.back()+section[0]);
    // The full checksum WORD is stored, but original AL subtracts only CL.
    // A difference of256 passes; neither key/header is overwritten by decode.
    return Byte(section[2]-sum(section));
}
void initialize_rows(Section& section) {
    for(std::size_t row=0;row<places;++row) {
        std::fill_n(section.begin()+names_offset+row*name_stride,name_length,gaiji_dot);
        section[names_offset+row*name_stride+name_length]=0;
        std::fill_n(section.begin()+digits_offset+row*8,8,gaiji_zero);
        if(row==0)section[digits_offset+5]=gaiji_zero+1;
        else section[digits_offset+row*8+4]=Byte(gaiji_zero+10-row);
        section[stages_offset+row]=Byte(0xa5-row/2);
    }
    section[cleared_offset]=0x19;
    // Keep key/checksum and all eleven unused payload bytes. On a missing
    // file fresh BSS supplies zero; after a corrupt read they retain that
    // decoded buffer's contents. Recreate never clears the whole struct.
}
void recreate(Section& section,File& file,const Random& next) {
    initialize_rows(section);file.open(OpenMode::create);
    for(std::size_t i=0;i<section_count;++i) {
        encode(section,next);file.write(section);decode(section);
    }
    file.close();
}
bool load_for(Section& section,File& file,Byte character,Byte rank,const Random& next) {
    if(file.exists()) {
        file.open(OpenMode::read);
        file.seek(unsigned(rank)*section_size,0);
        if(character)file.seek(character_sections*section_size,1);
        file.read(section);file.close();
        if(!decode(section))return false;
    }
    // Actual _scoredat_recreate has file_create/write/close, so a single bad
    // selected checksum replaces BOTH characters' entire ten-section file.
    recreate(section,file,next);return true;
}
void save(Section& section,File& file,Byte character,Byte rank,const Random& next) {
    encode(section,next);file.open(OpenMode::append);
    file.seek(unsigned(rank)*section_size,0);
    if(character)file.seek(character_sections*section_size,1);
    file.write(section);
    // Re-key every section, including the just-written selection. The final
    // work buffer is section9 ENCODED, not the selected editable table. There
    // are22 RNG draws, not2; nonselected decoded bytes and trailing data stay.
    for(std::size_t i=0;i<section_count;++i) {
        file.seek(i*section_size,0);file.read(section);
        decode(section);encode(section,next);
        file.seek(i*section_size,0);file.write(section);
    }
    file.close();
}
Byte insert(Section& section,const score::Digits& digits,Byte stage,Byte end) {
    int row=int(places)-1;
    for(;row>=0;--row) {
        int digit=7;
        for(;digit>=0;--digit) {
            // Stored gaiji subtraction is a SIGNED int. Values below A0 can
            // be negative; converting the difference to a byte changes rank.
            const int old=int(section[digits_offset+std::size_t(row)*8+digit])-gaiji_zero;
            if(int(digits[digit])>old)break;
            if(int(digits[digit])<old)break;
        }
        if(digit>=0 && int(digits[digit])<int(section[digits_offset+std::size_t(row)*8+digit])-gaiji_zero)break;
    }
    if(row==int(places)-1)return no_entry;
    const auto place=std::size_t(row+1);
    // Equality walks upward, so the new row precedes EVERY equal existing row.
    for(int source=int(places)-2;source>=int(place);--source) {
        std::copy_n(section.begin()+names_offset+std::size_t(source)*name_stride,name_length,
            section.begin()+names_offset+std::size_t(source+1)*name_stride);
        std::copy_n(section.begin()+digits_offset+std::size_t(source)*8,8,
            section.begin()+digits_offset+std::size_t(source+1)*8);
        section[stages_offset+source+1]=section[stages_offset+source];
    }
    std::fill_n(section.begin()+names_offset+place*name_stride,name_length,gaiji_dot);
    for(std::size_t digit=0;digit<8;++digit)section[digits_offset+place*8+digit]=Byte(digits[digit]+gaiji_zero);
    section[stages_offset+place]=end>=0xfd ? gaiji_all : Byte(stage+gaiji_zero+1);
    // The ninth name bytes, cleared mask and unused storage never shift.
    return Byte(place);
}
void encode_main(Section& section,const Random& next) {
    const auto checksum=sum(section);section[2]=Byte(checksum);section[3]=Byte(checksum>>8);
    const auto key=next();section[0]=Byte(key);section[1]=Byte(key>>8);
    Byte feedback=0;
    for(std::size_t i=section_size;i-->names_offset;) {
        section[i]=Byte(section[i]-section[0]-feedback);
        feedback=Byte(rotate_right3(section[i])^section[1]);
    }
}
void recreate_main(Section& section,File& file,const Random& next) {
    initialize_rows(section);file.open(OpenMode::create);
    for(std::size_t i=0;i<section_count;++i) {
        encode_main(section,next);file.write(section);decode(section);
    }
    file.close();
}
bool load_main(Section& section,File& file,Byte character,Byte rank,const Random& next) {
    if(file.exists()) {
        file.open(OpenMode::read);file.seek(unsigned(rank)*section_size,0);
        if(character==1)file.seek(character_sections*section_size,1);
        file.read(section);file.close();
        if(!decode(section))return false;
    }
    recreate_main(section,file,next);return true;
}
void save_main(Section& section,File& file,Byte character,Byte rank,const Random& next) {
    encode_main(section,next);file.open(OpenMode::append);
    file.seek(unsigned(rank)*section_size,0);
    if(character==1)file.seek(character_sections*section_size,1);
    file.write(section);file.close();
}
Byte continue_main(Section& section,File& file,Byte character,Byte rank,Byte stage,bool turbo,
                   const score::Digits& digits,const Random& next) {
    load_main(section,file,character,rank,next);
    if(!turbo)return no_entry;
    const auto place=insert(section,digits,stage==6 ? 0 : stage,0);
    if(place==no_entry)return place;
    constexpr std::array<Byte,8> name{0xac,0xb8,0xb7,0xbd,0xb2,0xb7,0xbe,0xae};
    std::copy(name.begin(),name.end(),section.begin()+names_offset+place*name_stride);
    save_main(section,file,character,rank,next);return place;
}
} // namespace th04::portable::score_file

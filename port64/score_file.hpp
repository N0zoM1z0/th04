#pragma once
#include "score.hpp"
#include <array>
#include <cstddef>
#include <cstdint>
#include <functional>
#include <string>
#include <utility>
#include <vector>

namespace th04::portable::score_file {
using Byte=std::uint8_t;
using Bytes=std::vector<Byte>;
constexpr std::size_t section_size=196,section_count=10,character_sections=5;
constexpr std::size_t names_offset=4,name_length=8,name_stride=9;
constexpr std::size_t digits_offset=94,cleared_offset=174,stages_offset=176,places=10;
constexpr Byte gaiji_zero=0xa0,gaiji_dot=0xc4,gaiji_all=0xe9,no_entry=0xff;
using Section=std::array<Byte,section_size>;
using Random=std::function<std::uint16_t()>;
enum class OpenMode { read,append,create };
enum class IO { exists,open,seek,read,write,close };
struct Operation { IO kind;int a=0,b=0;Bytes data{}; };

// A score file has ten independently encoded sections, not a host C++ struct.
// This byte owner also retains trailing bytes and short-read buffer contents.
// Host persistence can use its complete snapshot without touching the input HDI.
class File {
public:
    File(bool exists=false,Bytes contents={}):exists_(exists),bytes_(std::move(contents)) {}
    bool exists();
    void open(OpenMode);
    void seek(std::uint32_t offset,unsigned origin);
    void read(Section&);
    void write(const Section&);
    void close();
    bool present() const { return exists_; }
    bool changed() const { return changed_; }
    const Bytes& bytes() const { return bytes_; }
    const std::vector<Operation>& operations() const { return operations_; }
private:
    bool exists_=false,open_=false,changed_=false;
    std::size_t position_=0;
    OpenMode mode_=OpenMode::read;
    Bytes bytes_;
    std::vector<Operation> operations_;
};
void encode(Section&,const Random&);
Byte decode(Section&);
void initialize_rows(Section&);
void recreate(Section&,File&,const Random&);
// Both load failure paths recreate AND write all ten sections. They consume
// twenty process-local RNG draws; a successful load does not consume any.
bool load_for(Section&,File&,Byte character,Byte rank,const Random&);
void save(Section&,File&,Byte character,Byte rank,const Random&);
Byte insert(Section&,const score::Digits&,Byte stage,Byte end_sequence);
// MAIN takes both key bytes from one RNG word and saves only its selection.
void encode_main(Section&,const Random&);
void recreate_main(Section&,File&,const Random&);
bool load_main(Section&,File&,Byte character,Byte rank,const Random&);
void save_main(Section&,File&,Byte character,Byte rank,const Random&);
// Loads even without turbo. A ranked Continue name is written before reset.
Byte continue_main(Section&,File&,Byte character,Byte rank,Byte stage,bool turbo,
                   const score::Digits&,const Random&);
} // namespace th04::portable::score_file

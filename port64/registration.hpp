#pragma once
#include "score_file.hpp"
#include <array>
#include <cstdint>
#include <string>
#include <vector>

namespace th04::portable::registration {
using Byte=score_file::Byte;
constexpr std::uint16_t up=1,down=2,left=4,right=8,bomb=0x10,shot=0x20,cancel=0x1000,ok=0x2000;
constexpr Byte empty=2,space=0xcd,back=0xce,forward=0xcf,enter=0xd5;
extern const std::array<Byte,51> alphabet;
struct Run {
    Byte stage=0,rank=0,character_ascii='0',shot_type=0,turbo=1,end_sequence=0;
    score::Digits digits{};
};
enum class Kind { tone,access,pi_load,pi_palette,pi_put,pi_free,copy,bfnt,
    file,table,text,sound,song,fade,gaiji,name,wait,free_sprites,clear_text };
struct Event {
    Kind kind;
    int a=0,b=0,c=0,d=0;
    score_file::Bytes bytes{};
    std::string text{};
    score_file::Operation io{};
};
// Logical owner of the complete registration menu. Graphics/audio/fade/wait
// requests remain ordered commands for a scene to consume. This class does
// not render, advance a palette fade, persist a host file or replace OP.
// Call advance only for a keyboard iteration after the startup fade completes.
class Menu {
public:
    Menu(Run,score_file::File&,const score_file::Random&,std::uint16_t initial_keys=0);
    void advance(std::uint16_t held);
    bool finished() const { return finished_; }
    bool editable() const { return place_!=score_file::no_entry; }
    Byte rank() const { return rank_; }
    Byte character() const { return character_; }
    Byte place() const { return place_; }
    unsigned ticks() const { return ticks_; }
    int name_cursor() const { return cursor_; }
    int alphabet_column() const { return column_; }
    int alphabet_row() const { return row_; }
    std::uint16_t input_lock() const { return lock_; }
    Byte repeat_frames() const { return repeat_; }
    const score_file::Section& section() const { return section_; }
    const std::vector<Event>& events() const { return events_; }
private:
    void event(Kind,int a=0,int b=0,int c=0,int d=0,std::string text={});
    void flush_io();
    void table(Byte);
    void alphabet_cursor(int color);
    void redraw_name();
    void finish(bool acknowledgement);
    void erase_and_back();
    score_file::File* file_;
    score_file::Random random_;
    score_file::Section section_{};
    std::vector<Event> events_;
    std::size_t io_at_=0;
    Byte rank_=0,character_=0,place_=score_file::no_entry,repeat_=0;
    int cursor_=0,column_=0,row_=0;
    unsigned ticks_=0;
    std::uint16_t lock_=1,previous_keys_=0;
    bool finished_=false;
};
} // namespace th04::portable::registration

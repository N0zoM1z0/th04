#include "verdict.hpp"
#include <algorithm>
#include <stdexcept>

namespace th04::portable::verdict {
namespace {
constexpr std::uint32_t million=1000000;
// Bounded interpretation of a DWORD as signed TC4J long, without host
// implementation-defined narrowing or aliasing a uint32_t through long&.
std::int64_t signed_dword(std::uint32_t n) {
    return n<0x80000000u ? std::int64_t(n) : std::int64_t(n)-0x100000000LL;
}
const char* labels[]={
    "\x81\x40\x81\x40\x81\x40\x81\x40\x81\x40\x81\x40\x81\x40 \x98\x72\x91\x4f\x94\xbb\x92\xe8",
    "\x93\xef\x88\xd5\x93\x78", "\x8d\xc5\x8f\x49\x93\xbe\x93\x5f",
    "\x83\x7e\x83\x58\x89\xf1\x90\x94", "\x83\x7b\x83\x80\x8e\x67\x97\x70\x89\xf1\x90\x94",
    "\x83\x51\x81\x5b\x83\x80\x92\x42\x90\xac\x97\xa6",
    "\x88\xab\x97\xec\x91\xde\x8e\xa1\x97\xa6",
    "\x83\x41\x83\x43\x83\x65\x83\x80\x89\xf1\x8e\xfb\x97\xa6",
    "\x93\xbe\x93\x5f\x83\x41\x83\x43\x83\x65\x83\x80\x8d\xc5\x8d\x82\x93\x5f\x97\xa6",
    "\x8b\x43\x8d\x87\x82\xa2", "\x8f\x88\x97\x9d\x97\x8e\x82\xbf\x97\xa6",
    "\x82\xa0\x82\xc8\x82\xbd\x82\xcc\x98\x72\x91\x4f"
};
const char* ranks[]={
    "\x02\x02\x02\xae\xaa\xbc\xc2", "\x02\xb7\xb8\xbb\xb6\xaa\xb5",
    "\x02\x02\x02\xb1\xaa\xbb\xad", "\xb5\xbe\xb7\xaa\xbd\xb2\xac",
    "\x02\x02\xae\xc1\xbd\xbb\xaa"
};
constexpr const char* decimal="\x81\x44";
constexpr const char* percent="\x81\x93";
constexpr const char* point="\x93\x5f";
}
void Plan::emit(Kind k,int a,int b,int c,int d,int e,std::string data) {
    events_.push_back({k,a,b,c,d,e,std::move(data)});
}
void Plan::text(int x,int y,const std::string& s,int color) { emit(Kind::text,x,y,color,2,0,s); }
void Plan::gaiji(int x,int y,const std::string& s) {
    // Original graph_gaiji_puts walks a NUL-terminated byte string; even a
    // hundreds glyph that wraps to NUL terminates the whole draw request.
    emit(Kind::gaiji,x,y,16,14,0,s.substr(0,s.find('\0')));
}
void Plan::number(int x,int y,std::uint16_t n,bool fixed) {
    const unsigned hundreds=n/100,tens=(n%100)/10,ones=n%10;
    const char first=static_cast<char>(fixed || !hundreds ? 2 : std::uint8_t(0xa0+hundreds));
    const char second=static_cast<char>(!fixed && !hundreds && !tens ? 2 : 0xa0+tens);
    gaiji(x,y,std::string{first,second,static_cast<char>(0xa0+ones)});
}
void Plan::fraction(int x,int y,std::uint32_t n) {
    number(x,y,static_cast<std::uint16_t>(n/10000));
    number(x+48,y,static_cast<std::uint16_t>((n%10000)/100),true);
    text(x+48,y,decimal);
}
void Plan::percentage(int x,int y,std::uint16_t total,std::uint16_t share,bool subtract) {
    std::uint32_t n=total ? million : 0;
    // Preserve division before multiplication and the total==share shortcut.
    // Computing share*million/total changes the original integer rounding.
    if(total!=share) n=(total ? n/total : 0)*share;
    if(subtract)result_.skill-=n;else result_.skill+=n;
    fraction(x,y,n);text(x+96,y,percent);
}
Plan::Plan(const Input& input,const Bytes& commentary) {
    const auto& r=input.resident;
    const auto& s=r.statistics;
    const bool extra=r.stage==6;
    result_.rank=extra ? 4 : r.config.rank;
    if(result_.rank>4 || (!extra && result_.rank>3) || r.credit_lives<1 || r.credit_lives>6)
        throw std::invalid_argument("verdict requires a valid rank and starting lives");
    if(std::any_of(r.score_digits.begin(),r.score_digits.end(),[](auto d){return d>9;}))
        throw std::invalid_argument("verdict score is not eight BCD digits");
    result_.skill=input.initial_skill;
    result_.std_frames=s.std_frames;
    emit(Kind::tone,0);emit(Kind::access,1);
    emit(Kind::pi_load,0,0,0,0,0,"ude.pi");emit(Kind::pi_palette);emit(Kind::pi_put);
    emit(Kind::pi_free);emit(Kind::copy_page,0);emit(Kind::fade,0,1,4);
    emit(Kind::access,0);emit(Kind::show,0);
    for(unsigned i=0;i<12;++i)text(16,i<11 ? 48+int(i)*24 : 336,labels[i],15);
    gaiji(176,72,ranks[result_.rank]);
    std::string score;
    unsigned nonzero=0;
    for(unsigned i=8;i--;) {
        nonzero|=r.score_digits[i];
        score.push_back(static_cast<char>(nonzero ? 0xa0+r.score_digits[i] : 2));
    }
    gaiji(160,96,score);text(288,96,point);
    number(240,120,input.misses);number(240,144,input.bombs_used);
    text(288,120,"\x89\xf1");text(288,144,"\x89\xf1");
    if((!extra && r.end_sequence==application::EndSequence::good) ||
       (extra && r.end_sequence==application::EndSequence::extra))result_.std_frames=extra ? 12000 : 44000;
    // BB81 toggles BSS3F9C here, but percentage reads initialized DATA071A.
    // Those are different original addresses; the toggle does not negate
    // completion. Fresh natural MAINE percentages all add with DATA071A=0.
    percentage(192,168,extra ? 12000 : 44000,result_.std_frames,input.subtract_percentages);
    percentage(192,192,s.enemies_gone,s.enemies_killed,input.subtract_percentages);
    percentage(192,216,s.items_spawned,s.items_collected,input.subtract_percentages);
    percentage(192,240,s.point_items_collected,s.max_valued_point_items_collected,input.subtract_percentages);

    rng::Lcg32 random(r.random_seed_source);
    std::uint32_t bonus=(6-r.credit_lives)*500;
    if(!r.credit_bombs)bonus+=2500;else if(r.credit_bombs==1)bonus+=1500;
    if(r.config.turbo)bonus+=2000;
    // Original ADD AX,AX / MOVZX EAX,AX: wrap at 16 bits before promotion.
    bonus+=static_cast<std::uint16_t>(r.graze*2u);
    std::uint32_t recovered_items=million;
    if(s.items_spawned!=s.items_collected)
        recovered_items=(s.items_spawned ? recovered_items/s.items_spawned : 0)*s.items_collected;
    const std::uint32_t penalty=(million-recovered_items)/100;
    result_.random_drawn=penalty!=0;
    if(penalty)bonus+=random.next15()%penalty;
    bonus*=100;
    bonus=std::min(bonus,million);
    result_.random_state=random.state();
    result_.skill+=bonus;fraction(192,264,bonus);text(288,264,percent);
    // DIV by 10 occurs as DWORD, followed by PUSH AX: the rate helper then
    // receives only the low word, even for a very long run.
    percentage(192,288,static_cast<std::uint16_t>(s.frames/10),
               static_cast<std::uint16_t>(s.slow_frames/10),input.subtract_percentages);
    result_.skill=static_cast<std::uint32_t>(signed_dword(result_.skill)/5);
    if(r.score_digits[7]>=9)result_.skill+=600000;
    else {
        result_.skill+=r.score_digits[6]*10000u;
        if(r.score_digits[7]>3)result_.skill+=(r.score_digits[7]-3)*100000u;
    }
    switch(result_.rank) {
    case 0:result_.skill-=50000;result_.cap=800000;break;
    case 1:result_.cap=million;break;
    case 2:result_.skill+=150000;result_.cap=1200000;break;
    case 3:result_.skill+=300000;result_.cap=1400000;break;
    case 4:result_.skill+=450000;result_.cap=1500000;break;
    }
    switch(r.credit_lives) {
    case 1:result_.skill+=50000;result_.cap+=100000;break;
    case 2:result_.skill+=25000;result_.cap+=50000;break;
    case 4:result_.cap-=25000;break;
    case 5:result_.cap-=50000;break;
    case 6:result_.cap-=75000;break;
    }
    if(!r.credit_bombs) { result_.skill+=50000;result_.cap+=100000; }
    else if(r.credit_bombs==1) { result_.skill+=20000;result_.cap+=50000; }
    if(!r.config.turbo)result_.skill-=100000;
    result_.skill-=input.misses>=15 ? 300000 : input.misses*20000u;
    result_.skill-=input.bombs_used>=30 ? 90000 : input.bombs_used*3000u;
    if(static_cast<unsigned>(r.end_sequence)<0xfd) {
        if(extra)result_.skill-=200000;
        else result_.skill=static_cast<std::uint32_t>(signed_dword(result_.skill)/2);
    } else if(r.end_sequence==application::EndSequence::bad)result_.cap-=100000;
    result_.skill=signed_dword(result_.skill)<0 ? 0 : std::min(result_.skill,result_.cap);
    result_.score_visible=(s.frames>>1)>s.slow_frames;
    if(result_.score_visible) {
        fraction(192,336,result_.skill);text(288,336,point);
        emit(Kind::file_open,0,0,0,0,0,"_ude.txt");
        int line=0;
        if(result_.skill<1500000) {
            if(!result_.skill)line=25;
            else if(result_.skill<1050000)line=24-int(result_.skill/50000);
            else if(result_.skill<1200000)line=3;
            else if(result_.skill<1350000)line=2;
            else line=1;
            emit(Kind::file_seek,line*30);
        }
        result_.commentary_line=line;
        const unsigned at=unsigned(line)*30;
        if(commentary.size()<at+30)throw std::invalid_argument("verdict commentary record is truncated");
        std::string record(commentary.begin()+at,commentary.begin()+at+30);
        emit(Kind::file_read,30,0,0,0,0,record);emit(Kind::file_close);
        record[28]=0;
        emit(Kind::delay,64);text(64,360,record.substr(0,record.find('\0')),15);
    } else {
        text(192,336,"\x81\x48\x81\x48\x81\x48\x81\x48\x81\x48\x81\x48\x93\x5f");
        text(64,360,"\x8f\x88\x97\x9d\x97\x8e\x82\xbf\x82\xc9\x82\xe6\x82\xe9\x94\xbb\x92\xe8\x95\x73\x89\xc2",15);
    }
    emit(Kind::wait,0);emit(Kind::fade,0,0,2);
}
const char* kind_name(Kind k) {
    constexpr const char* names[]={"tone","access","show","pi_load","pi_palette","pi_put","pi_free","copy_page","fade",
        "text","gaiji","file_open","file_seek","file_read","file_close","delay","wait"};
    return names[static_cast<unsigned>(k)];
}
void Script::advance(std::uint16_t held,const Sink& sink) {
    if(status_==Status::stopped)return;
    ++ticks_;
    if(status_==Status::release || status_==Status::press) {
        // input_reset_sense samples before frame_delay(1); input_sense then
        // ORs the post-refresh sample. A one-refresh release between two
        // held samples cannot satisfy the original release loop.
        const auto sampled=static_cast<std::uint16_t>(previous_keys_|held);
        previous_keys_=held;
        if(status_==Status::release) { if(!sampled)status_=Status::press;return; }
        if(!sampled)return;
        status_=Status::running;
    }
    if(status_==Status::delay) {
        if(left_>0 && --left_>0)return;
        if(fade_step_) {
            tone_+=fade_step_;
            if((fade_step_>0 && tone_>=fade_end_) || (fade_step_<0 && tone_<=fade_end_)) {
                tone_=fade_end_;fade_step_=0;
            } else { left_=fade_speed_;return; }
        }
        status_=Status::running;
    }
    while(at_<plan_.requests().size()) {
        const auto& e=plan_.requests()[at_++];
        if(e.kind==Kind::tone)tone_=e.a;
        else if(e.kind==Kind::fade) {
            tone_=e.b ? 0 : 100;fade_end_=e.b ? 100 : 0;
            fade_step_=e.b ? 6 : -6;fade_speed_=e.c;left_=1+fade_speed_;status_=Status::delay;
        } else if(e.kind==Kind::delay) { left_=e.a;status_=Status::delay; }
        else if(e.kind==Kind::wait) { previous_keys_=held;status_=Status::release; }
        if(sink)sink(e);
        if(status_!=Status::running)return;
    }
    status_=Status::stopped;
}
} // namespace th04::portable::verdict

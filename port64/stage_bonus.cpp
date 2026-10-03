#include "stage_bonus.hpp"
#include "bonus_text.hpp"
#include <algorithm>
#include <array>

namespace th04::portable::bonus {
namespace {
std::string digits(std::uint32_t value,unsigned places,bool trailing_zero) {
    std::string result;std::uint32_t divisor=1;
    for(unsigned i=1;i<places;++i) divisor*=10;
    bool started=false;
    while(divisor>1) {
        const auto digit=value/divisor;value%=divisor;started=started || digit!=0;
        result.push_back(static_cast<char>(started ? digit+0xa0 : 2));divisor/=10;
    }
    result.push_back(static_cast<char>(value+0xa0));
    if(trailing_zero) result.push_back(static_cast<char>(0xa0));
    return result;
}
} // namespace
Result apply(const Context& c,State& s,bool all_clear) {
    Result r;
    const auto text=[&](int row,const std::string& bytes,int color=0xe1) {
        r.events.push_back({Kind::text,6,row,color,0,bytes});
    };
    const auto gaiji=[&](int left,int row,const std::string& bytes) {
        r.events.push_back({Kind::gaiji,left,row,0xe1,0,bytes});
    };
    const auto value=[&](int row,std::uint16_t n) { gaiji(34,row,digits(n,7,true)); };
    const auto performance=[&](unsigned amount,bool raise) {
        r.events.push_back({raise ? Kind::raise_performance : Kind::lower_performance,0,0,0,amount,{}});
        if(raise) s.performance=std::min(static_cast<std::uint8_t>(s.performance+amount),s.maximum);
        else {
            const auto lowered=static_cast<std::uint8_t>(s.performance-amount);
            const int signed_lowered=lowered<128 ? lowered : int(lowered)-256;
            const int signed_minimum=s.minimum<128 ? s.minimum : int(s.minimum)-256;
            s.performance=signed_lowered<signed_minimum ? s.minimum : lowered;
        }
    };
    s.palette_tone=60;r.events.push_back({Kind::tone,0,0,0,60,{}});
    if(all_clear) s.extends=10;
    gaiji(all_clear ? 19 : 20,4,all_clear ? text::gpCONGRATULATION : text::gpCLEAR_BONUS);
    const int first=all_clear ? 6 : 7;
    text(first,all_clear ? text::aALL_CLEAR : text::aBONUS_STAGE);
    text(first+2,text::aPOWERX50);text(first+4,text::aBONUS_DREAM);text(first+6,text::aGRAZEX50);
    if(all_clear) text(14,c.rank==4 ? text::aPLAYER_REM_30000 : text::aPLAYER_REM_10000);
    text(all_clear ? 17 : 16,text::aBONUS_POINT);text(21,text::aBONUS_TOTAL);
    if(!all_clear) text(22,text::aBOMB_EXTEND,0xc3);

    // Every component first passes through original unsigned int (16 bits).
    // In particular graze*5 and the all-clear life term wrap BEFORE widening.
    auto component=static_cast<std::uint16_t>(all_clear ? 1000 : (unsigned(c.stage)+1)*100);
    std::uint32_t points=component;value(first,component);
    component=static_cast<std::uint16_t>(unsigned(c.power)*5);points+=component;value(first+2,component);
    points+=c.dream;value(first+4,c.dream);
    component=static_cast<std::uint16_t>(unsigned(c.graze)*5);points+=component;value(first+6,component);
    if(all_clear) {
        const unsigned multiplier=c.rank==4 ? 3000 : 1000;
        component=static_cast<std::uint16_t>(unsigned(c.remaining_lives)*multiplier-multiplier);
        points+=component;value(14,component);
    }
    points*=c.point_items;gaiji(40,all_clear ? 17 : 16,digits(c.point_items,5,false));
    r.before_modifiers=points;
    const auto factor=[&](int row,unsigned n,const std::string& description) {
        // Three separate unsigned-long multiply/divide operations, each with
        // its own truncation. Combining factors changes low-point rewards.
        points*=n;points/=10;text(row,description,n<10 ? 0x41 : 0x81);
    };
    if(!c.defeated_in_time) factor(20,0,text::aBOSS_FINAL_TIMEOUT);
    else {
        switch(c.credit_lives) {
        case 6:factor(18,3,text::aPENALTY_6);break;
        case 5:factor(18,5,text::aPENALTY_5);break;
        case 4:factor(18,7,text::aPENALTY_4);break;
        default:break;
        }
        switch(c.continues) {
        case 1:factor(19,8,text::aPENALTY_CONT_1);break;
        case 2:factor(19,6,text::aPENALTY_CONT_2);break;
        case 3:factor(19,4,text::aPENALTY_CONT_3);break;
        default:break;
        }
        switch(c.rank) {
        case 0:factor(20,5,text::aBONUS_EASY);break;
        case 1:factor(20,10,text::aBONUS_NORMAL);break;
        case 2:factor(20,12,text::aBONUS_HARD);break;
        case 3:factor(20,14,text::aBONUS_LUNATIC);break;
        default:break; // Extra has no rank multiplier.
        }
    }
    r.awarded=points;gaiji(34,21,digits(points,7,true));s.score_delta+=points;
    if(!all_clear) {
        // Performance uses the UNMODIFIED subtotal even after a timeout.
        if(r.before_modifiers>=1200000) performance(4,true);
        else if(r.before_modifiers>=800000) performance(2,true);
        else if(r.before_modifiers>=500000) performance(1,true);
        else if(r.before_modifiers<=100000) performance(2,false);
        else if(r.before_modifiers<=200000) performance(1,false);
        ++s.bombs;r.events.push_back({Kind::hud_bombs,0,0,0,0,{}});
        if(c.misses<=c.resource_stage) performance(2,true);
        if(unsigned(c.bombs_used)<=unsigned(c.resource_stage)*2) performance(2,true);
    }
    return r;
}
} // namespace th04::portable::bonus

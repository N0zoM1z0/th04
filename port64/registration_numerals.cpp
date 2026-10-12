#include "registration_numerals.hpp"
#include <stdexcept>
namespace th04::portable::registration::numerals {
Slot address(std::uint16_t pattern) {
    const auto scaled=std::uint16_t(pattern*2u);
    return {pattern,std::uint16_t(0x0f0cu+scaled),std::uint16_t(0x130cu+scaled)};
}
std::vector<Request> row(const score::Digits& digits,unsigned place,bool selected,std::uint8_t character) {
    if(place>=10 || character>=2)throw std::invalid_argument("registration numeral row ownership");
    std::vector<Request> result;
    const int top=place ? int(place)*16+112 : 96;
    int left=character ? 480 : 172;
    const int bank=selected ? 10 : 0,high=int(digits[7])-0xa0;
    const auto put=[&](int x,int pattern){result.push_back({std::uint16_t(x),std::uint16_t(top),address(std::uint16_t(pattern))});};
    if(high>=10)put(left-32,high/10+bank);
    // Turbo C++ signed IDIV truncates toward zero. A negative high byte can
    // still have a legal remainder; lower bytes pass the raw WORD directly.
    put(left-16,high%10+bank);
    for(int digit=6;digit>=0;--digit,left+=16)put(left,int(digits[unsigned(digit)])+bank-0xa0);
    return result;
}
}

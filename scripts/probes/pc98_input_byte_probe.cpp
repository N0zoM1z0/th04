#include "pc98_input.hpp"
#include <iostream>
#include <sstream>
#include <string>
namespace input=th04::portable::pc98_input;
int main() {
    input::Latch latch;char operation;std::string bytes;unsigned shift,enabled,pins;
    while(std::cin>>operation>>bytes>>shift>>enabled>>pins) {
        input::BiosKeys keys{};
        for(unsigned i=0;i<10;++i)keys[i]=std::uint8_t(std::stoul(bytes.substr(2*i,2),nullptr,16));
        std::ostringstream trace;
        const auto point=[&](const std::string& name) {
            trace<<name<<':'<<latch.actions()<<':'<<unsigned(latch.shift())<<',';
        };
        input::ByteSource source{[&](input::Operation){point("B");},
            [&](unsigned group){point("K"+std::to_string(group));return keys[group];},
            [&]{point("H");return shift!=0;}};
#ifdef JOYSTICK_BYTE_SOURCE
        source.joystick_enabled=[&]{point("E");return enabled!=0;};
        source.joystick_pins=[&]{point("J");return std::uint8_t(pins);};
#endif
        const auto sample=latch.poll(operation=='R'?input::Operation::reset:input::Operation::sense,source);
        std::cout<<latch.actions()<<' '<<unsigned(latch.shift())<<' '
            <<unsigned(sample.joystick_enabled)<<' '<<unsigned(sample.joystick_pins)<<' '<<trace.str()<<'\n';
    }
    return std::cin.eof()?0:1;
}

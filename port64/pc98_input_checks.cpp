#include "pc98_input.hpp"
#include <iostream>
#include <stdexcept>
using namespace th04::portable::pc98_input;
namespace {
void require(bool condition,const char* message) {
    if(!condition)throw std::runtime_error(message);
}
}
int main() {
    try {
        Latch input;
        require(input.actions()==0 && !input.shift(),"initial latch");
        Sample enter;enter.keys[3]=0x10;
        input.reset_sense(enter);
        require(input.actions()==0x2000,"Enter at tail reset sample");
        Sample released;
        input.sense(released);
        require(input.actions()==0x2000,"head sample preserves released Enter");
        input.reset_sense(released);
        require(input.actions()==0,"next reset clears released Enter");
        Sample shot;shot.keys[5]=0x02;shot.shift=true;
        input.reset_sense(shot);
        input.sense(released);
        require(input.actions()==0x20 && !input.shift(),"actions accumulate but Shift is replaced");
        Sample keypad;keypad.keys[9]=0x04;
        input.reset_sense(keypad);
        require(input.actions()==0x0400,"keypad diagonal retains distinct action");
        Sample arrows;arrows.keys[7]=0x28;
        input.sense(arrows);
        require(input.actions()==0x0406,"head arrows accumulate with keypad diagonal");
        Sample joystick;joystick.joystick_pins=0;
        input.reset_sense(joystick);
        require(input.actions()==0,"disabled joystick ignores pins");
        joystick.joystick_enabled=true;
        input.sense(joystick);
        require(input.actions()==0x003f,"joystick contributes only low six actions");
        joystick.joystick_pins=0xff;
        input.sense(joystick);
        require(input.actions()==0x003f,"joystick release preserves latch until reset");
        input.reset_sense(joystick);
        require(input.actions()==0,"reset samples released active-low pins");
        Sample all;all.keys.fill(0xff);all.shift=true;
        input.reset_sense(all);
        require(input.actions()==0x7f3f && input.shift(),"complete keyboard action domain");
        unsigned reads=0;
        const std::array<unsigned,8> groups{{7,9,8,5,2,0,3,6}};
        const std::array<std::uint8_t,8> bytes{{4,4,0x40,2,1,1,0x10,0x10}};
        const std::array<std::uint16_t,8> prior{{0,1,0x401,0x405,0x425,0x4425,0x5425,0x7425}};
        ByteSource source{[&](Operation op) {
            require(op==Operation::reset && !input.actions(),"reset must precede the first physical read");
        },[&](unsigned group) {
            require(reads<8 && group==groups[reads],"original scalar read order");
            require(input.actions()==prior[reads] && input.shift(),"each read must see the preceding OR and prior Shift");
            return bytes[reads++];
        },[&] {require(reads==8 && input.actions()==0x7425,"Shift follows all scalar ORs");return false;}};
        const auto sampled=input.poll(Operation::reset,source);
        require(input.actions()==0x7425 && !input.shift() && sampled.keys[5]==2,"independent byte sample reaches latch");
        ByteSource empty{{},[](unsigned){return std::uint8_t(0);},[]{return false;}};
        input.poll(Operation::sense,empty);require(input.actions()==0x7425,"byte Sense preserves the latch after physical release");
        input.poll(Operation::reset,empty);require(!input.actions(),"byte Reset clears before fresh reads");
        std::cout<<"PC-98 input sampler contracts pass\n";
        return 0;
    } catch(const std::exception& error) {
        std::cerr<<error.what()<<'\n';return 1;
    }
}

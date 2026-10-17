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
        std::cout<<"PC-98 input sampler contracts pass\n";
        return 0;
    } catch(const std::exception& error) {
        std::cerr<<error.what()<<'\n';return 1;
    }
}

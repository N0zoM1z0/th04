#pragma once
#include "motion.hpp"
#include <cstdint>
#include <functional>
#include <vector>

namespace th04::portable::transition {
enum class Callback : std::uint8_t { none,enter,leave,titles };
struct Overlay { std::uint8_t time=0;Callback callback=Callback::enter; };
enum class TextKind : std::uint8_t { character,gaiji };
struct Text { TextKind kind{};unsigned left=0,row=0,value=0,attribute=0; };
// The enter and leave callbacks share ONE byte. Enter leaves it at72;
// leave decrements it before selecting a cel and clears the callback only
// on the following zero-time call. Titles remain a separate consumer.
std::vector<Text> update_overlay(Overlay&);
struct Departure {
    std::int16_t frame=0;
    std::uint16_t graze=0,stage_graze=0;
    std::uint8_t stage=0,stage_ascii='0',quit=0;
    std::int16_t palette_tone=100;
    std::uint8_t palette_changed=0;
    motion::Point homing{};
    bool blocked=false;
};
enum class Kind { tone,dialog,bonus,fade,next_stage,delay,all_clear,end_game };
struct Event { Kind kind{};unsigned value=0; };
using Sink=std::function<void(const Event&)>;
// Ordinary Stage1 departure. Caller can suspend at the actual dialog call.
// Resuming continues AFTER that call, without repeating tone/graze/prefix.
// Final/Extra Ending dispatch is a distinct owner, not handled here.
void update_departure(Departure&,Overlay&,bool suspend_dialog=false,const Sink& sink={});
// Final Stage (stage_id5) uses all-clear at0 and the nonreturning end_game
// call at416. Return true at that call boundary: no frame increment, homing
// reset, leave fade, next-stage publication or actor-frame suffix follows it.
bool update_final_departure(Departure&,const Sink& sink={});
} // namespace th04::portable::transition

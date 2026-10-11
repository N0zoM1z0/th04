#pragma once
#include "motion.hpp"
#include <functional>
#include <optional>

namespace th04::portable::grcg {
enum class Kind : std::uint8_t {point,horizontal_line};
struct Request {
    Kind kind;
    std::int16_t left,right,y;
};
using Sink=std::function<void(const Request&)>;
// MAIN0000:114C. Emit the original ordered PSET/HLINE calls, including
// duplicate spans and unsigned WORD radii. Clipping belongs to the callees.
void circlefill(motion::Point center,std::uint16_t radius,const Sink&);
// MAIN0000:14DC with TH04's stage clip X32..415/Y16..383. Endpoint
// subtraction wraps before signed sorting; the result is inclusive.
std::optional<Request> stage_hline(std::int16_t left,std::int16_t right,std::int16_t y);
bool stage_pset(motion::Point);
}

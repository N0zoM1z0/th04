#pragma once
#include <cstdint>
#include <string>
#include <vector>
namespace th04::portable::extra_dialog {
enum class Kind {free,faces,bomb};
struct Resource {Kind kind{};unsigned slot=0;std::string name;unsigned image=0;};
// Native caches replace the DOS file/EMS consumer. Original non-EMS request
// order and the byte-valued Extra exit counter remain owned here.
class Resources {
public:
    explicit Resources(std::uint8_t calls=0):calls_(calls) {}
    std::uint8_t calls() const {return calls_;}
    std::vector<Resource> begin(unsigned character) const;
    std::vector<Resource> finish(unsigned character);
private:
    std::uint8_t calls_=0;
};
}

#pragma once
#include "pmd_pcm.hpp"
#include "sound_control.hpp"
#include <optional>

namespace th04::portable::sound {
struct PmdProfile {
    pmd::Board board=pmd::Board::fm26;
    std::uint32_t master_hz=4000000;
    pmd::Bytes rhythm_rom;
};
// Application-resident owner, separate from process-local control and beeper.
// This bounded service surface uses typed buffers instead of DOS far pointers.
// MMD, external ADPCM/PPS and an audio device remain separate owners.
class ResidentPmd {
public:
    explicit ResidentPmd(PmdProfile);
    ResidentPmd(const ResidentPmd&)=delete;ResidentPmd& operator=(const ResidentPmd&)=delete;
    Drivers drivers() const;
    std::uint16_t command(std::uint16_t);
    using Reader=std::function<std::optional<pmd::Bytes>(const std::string&)>;
    std::optional<int> consume(const Request&,const Reader&);
    std::vector<pmd::StereoSample> advance(std::uint64_t nanoseconds);
    const pmd::PcmPlayer& player() const {return player_;}
    const std::vector<pmd::FmWrite>& installation() const {return installation_;}
    bool file_open() const {return open_;}
private:
    pmd::Board board_;std::vector<pmd::StereoSample> samples_;
    pmd::PcmPlayer player_;std::vector<pmd::FmWrite> installation_;
    enum class Buffer {none,music,effects};
    Buffer destination_=Buffer::none;bool open_=false;
    std::string filename_;std::optional<pmd::Bytes> file_;
    void install();void write(unsigned bank,unsigned address,unsigned value);
};
}

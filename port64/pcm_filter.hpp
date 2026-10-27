#pragma once
#include <array>
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <stdexcept>
#include <vector>

namespace th04::portable::pmd {
// Causal fractional-delay low-pass. The chip is sampled above its SSG clock;
// only the 48 kHz outputs run the convolution. Coefficients are mathematical
// Kaiser-windowed sinc values, independent of game data or recorded waveforms.
class PcmFilter {
    static constexpr unsigned taps=256;
    static constexpr std::int64_t unit=std::int64_t(1)<<30;
    std::vector<std::array<std::int32_t,taps>> coefficients_;
    std::array<std::array<std::int32_t,taps*2>,2> history_{};
    unsigned head_=0;
    static double bessel(double x) {
        double sum=1,term=1;
        for(unsigned n=1;n<32;++n){term*=x*x/(4.0*n*n);sum+=term;if(term<sum*1e-16)break;}
        return sum;
    }
public:
    PcmFilter(std::uint32_t hz,unsigned step):coefficients_(step) {
        if(!hz || !step)throw std::invalid_argument("PCM filter clock");
        constexpr double pi=3.1415926535897932384626433832795,beta=8.6;
        const double rate=double(hz)/step,cutoff=std::min(20000.0,rate*0.45)/rate;
        const double norm=bessel(beta);
        for(unsigned phase=0;phase<step;++phase) {
            std::array<double,taps> values{};double sum=0;
            for(unsigned k=0;k<taps;++k) {
                const double position=double(k)-(taps-1)*0.5+double(phase)/step;
                const double x=2*pi*cutoff*position;
                const double sinc=std::abs(x)<1e-12 ? 1 : std::sin(x)/x;
                const double w=2*double(k)/(taps-1)-1;
                values[k]=2*cutoff*sinc*bessel(beta*std::sqrt(std::max(0.0,1-w*w)))/norm;
                sum+=values[k];
            }
            std::int64_t total=0;
            for(unsigned k=0;k<taps;++k){coefficients_[phase][k]=std::int32_t(std::llround(values[k]*unit/sum));total+=coefficients_[phase][k];}
            coefficients_[phase][taps/2]+=std::int32_t(unit-total);
        }
    }
    void push(std::int32_t left,std::int32_t right) {
        head_=(head_+taps-1)%taps;
        history_[0][head_]=history_[0][head_+taps]=left;
        history_[1][head_]=history_[1][head_+taps]=right;
    }
    std::int32_t sample(unsigned channel,unsigned phase) const {
        const auto& coefficients=coefficients_.at(phase);
        const auto* input=history_.at(channel).data()+head_;std::int64_t sum=0;
        for(unsigned k=0;k<taps;++k)sum+=std::int64_t(input[k])*coefficients[k];
        return std::int32_t(sum>=0 ? (sum+unit/2)/unit : -((-sum+unit/2)/unit));
    }
};
}

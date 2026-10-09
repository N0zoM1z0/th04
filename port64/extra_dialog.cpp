#include "extra_dialog.hpp"
namespace th04::portable::extra_dialog {
std::vector<Resource> Resources::begin(unsigned character) const {
    return {{Kind::free,0,{}},{Kind::faces,2,character ? "KAO1.cd2" : "KAO0.cd2"}};
}
std::vector<Resource> Resources::finish(unsigned character) {
    std::vector<Resource> requests;
    for(unsigned i=2;i<8;++i)requests.push_back({Kind::free,i,{}});
    for(unsigned i=8;i<11;++i)requests.push_back({Kind::free,i,{}});
    const auto previous=calls_++;
    requests.push_back({Kind::faces,8,previous ? "bss8.cd2" : "bss7.cd2"});
    requests.push_back({Kind::bomb,0,character ? "bb1.cdg" : "bb0.cdg"});
    return requests;
}
}

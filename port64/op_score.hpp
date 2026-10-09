#pragma once
#include "score_file.hpp"
#include "selection_state.hpp"

namespace th04::portable::op_score {
using Cleared=std::array<std::array<score_file::Byte,5>,2>;
struct Snapshot {
    score_file::Section first{},second{};
    Cleared cleared{};
    score_file::Byte rank=0,extra_unlocked=0;
};
// OP's decoder checks the complete first checksum WORD, then only the low
// second checksum BYTE. A first-column failure leaves the second untouched.
score_file::Byte decode_both(score_file::Section&,score_file::Section&);
class State {
public:
    explicit State(Snapshot snapshot={}):snapshot_(std::move(snapshot)) {}
    // Failure recreates ten sections and stops the rank scan. Prior accepted
    // ranks and the accumulated Extra flag remain in this OP process.
    void read(score_file::File&,score_file::Byte configured_rank,const score_file::Random&);
    bool load_both(score_file::File&,const score_file::Random&);
    void recreate(score_file::File&,const score_file::Random&);
    const Snapshot& snapshot() const {return snapshot_;}
    void browse_rank(score_file::Byte rank);
    bool extra_unlocked() const {return snapshot_.extra_unlocked!=0;}
    selection::Availability availability(bool extra) const;
private:
    Snapshot snapshot_;
};
}

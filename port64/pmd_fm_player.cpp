#include "pmd_fm_player.hpp"
namespace th04::portable::pmd {
FmPlayer::FmPlayer(Board board,FmSink sink):sink_(std::move(sink)),
    music_(board,[this](FmWrite w){effects_.mirror(w.bank,w.address,w.value);if(sink_)sink_(w);}),
    effects_(board,[this](FmWrite w){music_.mirror(w.bank,w.address,w.value);if(sink_)sink_(w);},[this]{music_.restore_effect_voice();}) {
    music_.effects_active([this]{return effects_.state().active;});
}
void FmPlayer::sync_masks(){
    std::array<std::uint8_t,6> masks{};
    for(unsigned p=0;p<6;++p)masks[p]=music_.sequence().state().parts[p].mask;
    effects_.musical_masks(masks);
}
void FmPlayer::start_effect(unsigned id){effects_.start(id);music_.borrow_effect();sync_masks();}
void FmPlayer::interrupt(std::uint8_t flags){music_.interrupt(flags);if(flags&1)effects_.timer_a();sync_masks();}
}

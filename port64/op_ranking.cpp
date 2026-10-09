#include "op_ranking.hpp"
#include <algorithm>
#include <stdexcept>

namespace th04::portable::op_ranking {
namespace sf=score_file;
namespace {
sf::Bytes bytes(const char* s) {return sf::Bytes(s,s+std::char_traits<char>::length(s));}
bool out(Phase p) {return p==Phase::entry_out || p==Phase::exit_out;}
}
const char* kind_name(Kind k) {
    constexpr const char* names[]={"sound","song","fade","vsync","tone","poll","delay","file","load","palette","picture","free","access","copy","name","gaiji","sprite"};
    return names[unsigned(k)];
}
Scene::Scene(op_score::State& state,sf::File& file,sf::Byte configured,
             sf::Random random,FileSink file_sink,Sink sink)
    :state_(state),file_(file),random_(std::move(random)),file_sink_(std::move(file_sink)),
     sink_(std::move(sink)),configured_(configured) {
    if(configured>=5)throw std::invalid_argument("OP configured ranking");
    emit(Kind::sound,0x100);emit(Kind::song,0x600,0,0,0,bytes("name"));
    emit(Kind::sound,0);emit(Kind::sound,0x280);fade(Phase::entry_out);
}
void Scene::emit(Kind kind,int a,int b,int c,int d,sf::Bytes data) {
    if(sink_)sink_({kind,ticks_,a,b,c,d,std::move(data)});
}
void Scene::fade(Phase p) {
    phase_=p;fade_ticks_=0;tone_=out(p) ? 100 : 0;
    emit(Kind::fade,out(p),1);emit(Kind::vsync);
}
void Scene::load() {
    const auto before=file_.operations().size();state_.load_both(file_,random_);
    for(std::size_t i=before;i<file_.operations().size();++i) {
        const auto& operation=file_.operations()[i];
        if(file_sink_)file_sink_(operation);
        emit(Kind::file,int(operation.kind),int(operation.a),int(operation.b),0,operation.data);
    }
}
void Scene::render() {
    for(int page:{1,0}) {
        emit(Kind::access,page);emit(Kind::palette);emit(Kind::picture);
    }
    const auto& s=state_.snapshot();
    for(unsigned place=0;place<sf::places;++place) {
        const int y=place ? int(place)*16+112 : 96;
        for(unsigned column=0;column<2;++column) {
            const auto& section=column ? s.second : s.first;
            const auto start=section.begin()+sf::names_offset+place*sf::name_stride;
            const auto end=std::find(start,section.end(),sf::Byte(0));
            if(end==section.end())throw std::invalid_argument("OP name lacks terminator in section");
            const sf::Bytes name(start,end);const int x=column ? 320 : 8;
            emit(Kind::name,x+2,y+2,16,14,name);
            emit(Kind::name,x,y,16,place ? 2 : 7,name);
        }
        const int first=int(s.first[sf::digits_offset+place*8+7])-0xa0;
        const int second=int(s.second[sf::digits_offset+place*8+7])-0xa0;
        if(first>=10)emit(Kind::sprite,140,y,first/10);
        if(second>=10)emit(Kind::sprite,448,y,second/10);
        emit(Kind::sprite,156,y,first%10);emit(Kind::sprite,464,y,second%10);
        for(int digit=6,left=16;digit>=0;--digit,left+=16) {
            emit(Kind::sprite,156+left,y,int(s.first[sf::digits_offset+place*8+unsigned(digit)])-0xa0);
            emit(Kind::sprite,464+left,y,int(s.second[sf::digits_offset+place*8+unsigned(digit)])-0xa0);
        }
        for(unsigned column=0;column<2;++column) {
            const auto glyph=(column ? s.second : s.first)[sf::stages_offset+place];
            const int x=column ? 600 : 292,g=glyph==0xff ? 0xef : int(glyph);
            emit(Kind::gaiji,x+2,y+2,g,14);emit(Kind::gaiji,x,y,g,7);
        }
    }
    emit(Kind::sprite,496,376,10+int(s.rank)*2);
    emit(Kind::sprite,560,376,11+int(s.rank)*2);
}
void Scene::poll(std::uint16_t held,Phase p) {
    sampled_=held;phase_=p;emit(Kind::poll,held);emit(Kind::delay,1);
}
void Scene::browse(int rank,Phase p) {
    state_.browse_rank(sf::Byte(rank));tone_=0;emit(Kind::tone,0);
    load();render();fade(p);
}
void Scene::right(std::uint16_t held) {
    if((sampled_&8) && state_.snapshot().rank<4)browse(int(state_.snapshot().rank)+1,Phase::right_in);
    else poll(held);
}
void Scene::after_fade(std::uint16_t held) {
    switch(phase_) {
    case Phase::entry_out:
        state_.browse_rank(configured_);load();emit(Kind::load,0,0,0,0,bytes("hi01.pi"));render();fade(Phase::entry_in);break;
    case Phase::entry_in:case Phase::right_in:poll(held);break;
    case Phase::left_in:right(held);break;
    case Phase::exit_out:
        emit(Kind::free);emit(Kind::access,1);emit(Kind::load,0,0,0,0,bytes("op1.pi"));
        emit(Kind::palette);emit(Kind::picture);emit(Kind::free);emit(Kind::copy,0);fade(Phase::exit_in);break;
    case Phase::exit_in:poll(held,Phase::release);break;
    default:throw std::logic_error("OP ranking fade phase");
    }
}
void Scene::advance(std::uint16_t held) {
    if(finished())return;
    ++ticks_;
    if(phase_==Phase::poll) {
        if(sampled_&0x3020) {emit(Kind::sound,0x201);fade(Phase::exit_out);}
        else if((sampled_&4) && state_.snapshot().rank)browse(int(state_.snapshot().rank)-1,Phase::left_in);
        else right(held);
    } else if(phase_==Phase::release) {
        if(sampled_)poll(held,Phase::release);
        else {
            emit(Kind::sound,0x100);emit(Kind::song,0x600,0,0,0,bytes("op"));emit(Kind::sound,0);
            phase_=Phase::stopped;
        }
    } else {
        ++fade_ticks_;const int progress=fade_ticks_==18 ? 100 : int(fade_ticks_-1)*6;
        tone_=out(phase_) ? 100-progress : progress;emit(Kind::tone,tone_);
        if(fade_ticks_==18)after_fade(held);else emit(Kind::vsync);
    }
}
Renderer::Renderer(const Assets& a,std::array<sf::Bytes,2> pages,unsigned shown)
    :canvas_(a.graphics,std::move(pages),shown),numerals_(a.numerals),labels_(a.rank_labels) {
    if(numerals_.width()!=16 || numerals_.height()!=16 || numerals_.count()!=10 ||
       labels_.width()!=64 || labels_.height()!=16 || labels_.count()!=10)
        throw std::invalid_argument("OP SCNUM/HI_M geometry");
    cutscene::Event load(cutscene::Kind::pi_load);load.name="OP1.PI";
    canvas_.apply(load);canvas_.apply({cutscene::Kind::pi_palette});canvas_.apply({cutscene::Kind::pi_free});
}
void Renderer::apply(const Event& e) {
    using K=cutscene::Kind;
    if(e.kind==Kind::name)canvas_.put_gaiji(e.a,e.b,std::string(e.data.begin(),e.data.end()),e.c,unsigned(e.d));
    else if(e.kind==Kind::gaiji)canvas_.apply({cutscene::Kind::gaiji,e.a,e.b,e.c,e.d});
    else if(e.kind==Kind::sprite) {
        if(e.c<0 || e.c>=20)throw std::out_of_range("OP undefined SUPER pattern");
        const auto& sheet=e.c<10 ? numerals_ : labels_;const unsigned image=unsigned(e.c<10 ? e.c : e.c-10);
        auto& page=canvas_.drawing_page();
        for(unsigned y=0;y<sheet.height();++y)for(unsigned x=0;x<sheet.width();++x) {
            const auto color=sheet.pixel(image,x,y);const int px=e.a+int(x),py=e.b+int(y);
            if(color && px>=0 && px<640 && py>=0 && py<400)page[unsigned(py)*640+unsigned(px)]=color;
        }
    } else {
        K kind;
        switch(e.kind) {
        case Kind::load:kind=K::pi_load;break;
        case Kind::palette:kind=K::pi_palette;break;
        case Kind::picture:kind=K::pi_put;break;
        case Kind::free:kind=K::pi_free;break;
        case Kind::access:kind=K::access;break;
        case Kind::copy:kind=K::copy_page;break;
        default:return;
        }
        cutscene::Event request(kind,e.a,e.b);request.name=std::string(e.data.begin(),e.data.end());canvas_.apply(request);
    }
}
sf::Bytes Renderer::rgb(unsigned page,int tone) const {
    if(tone<0 || tone>100)throw std::out_of_range("OP palette tone");
    sf::Bytes result;result.reserve(640*400*3);
    for(auto pixel:canvas_.page(page))for(unsigned channel=0;channel<3;++channel)
        result.push_back(sf::Byte(((unsigned(canvas_.palette()[unsigned(pixel)*3+channel])>>4)*unsigned(tone)/100u)*17u));
    return result;
}
} // namespace th04::portable::op_ranking

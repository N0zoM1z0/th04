#include "op_startup.hpp"
#include <algorithm>
#include <stdexcept>

namespace th04::portable::op_startup {
const char* kind_name(Kind k) {
    constexpr const char* names[]={"access","show","load","palette","picture","free","copy","clear","fill","snap","restore",
        "bg_free","super_load","super_free","sprite","song","command","measure","reset","sense","wait","palette_show","se","se_update","logo_complete","complete"};
    return names[unsigned(k)];
}
namespace {
Bytes text(const char* s) {return Bytes(s,s+std::char_traits<char>::length(s));}
constexpr const char* slides[]={"op5b.pi","op4b.pi","op3b.pi","op2b.pi","op1b.pi","op0b.pi"};
constexpr const char* fireworks[]={"zun02.bft","zun04.bft","zun01.bft","zun03.bft"};
}
Scene::Scene(const Assets& assets,bool logo,bool demo,Sink sink,Measure measure,std::uint32_t seed,std::uint16_t initial_held,Palette initial_palette)
    :assets_(assets),sink_(std::move(sink)),measure_(std::move(measure)),random_(seed),palette_(initial_palette),held_(initial_held),demo_(demo) {
    queue([this,logo]{if(logo)start_logo();else start_title();});drain();
}
void Scene::emit(Kind k,int a,int b,int c,Bytes data) {if(sink_)sink_({k,tick_,a,b,c,std::move(data)});}
void Scene::queue(std::function<void()> task) {tasks_.push_back(std::move(task));}
void Scene::drain() {
    while(!waiting_ && !measure_wait_ && !tasks_.empty()) {auto task=std::move(tasks_.front());tasks_.pop_front();task();}
}
void Scene::wait(unsigned n) {if(!n)throw std::logic_error("startup empty wait");emit(Kind::wait,int(n));waiting_=n;}
void Scene::advance(std::uint16_t held) {
    if(finished_)return;
    ++tick_;held_=held;
    if(measure_wait_) {
        const auto value=measure_ ? measure_() : std::nullopt;
        if(value && *value<2)return;
        measure_wait_=false;logo_ready();
    } else if(waiting_)--waiting_;
    drain();
}
void Scene::palette_show() {emit(Kind::palette_show,tone_,0,0,Bytes(palette_.begin(),palette_.end()));}
void Scene::apply_palette(const PiImage& image,unsigned slot) {palette_=image.palette;emit(Kind::palette,int(slot));palette_show();}
void Scene::fade(bool in,unsigned speed,std::function<void()> after) {
    tone_=in ? 0 : 100;
    queue([this]{wait(1);});
    for(int tone=in ? 0 : 100;in ? tone<100 : tone>0;tone+=in ? 6 : -6) {
        queue([this,tone]{tone_=tone;palette_show();});
        for(unsigned i=0;i<speed;++i)queue([this]{wait(1);});
    }
    queue([this,in,after=std::move(after)]{tone_=in ? 100 : 0;palette_show();after();});
}
void Scene::start_logo() {
    tone_=0;palette_show();emit(Kind::access,1);emit(Kind::load,0,0,0,text("zun00.pi"));
    apply_palette(assets_.logo,0);emit(Kind::picture,0,0,0);emit(Kind::free,0);emit(Kind::copy,0);emit(Kind::snap);
    emit(Kind::access,1);emit(Kind::clear);emit(Kind::access,0);emit(Kind::clear);
    logo_palette_=palette_;std::fill_n(palette_.begin(),45,0);
    emit(Kind::song,0x600,0,0,text("logo"));emit(Kind::command,0);
    // Only the first WORD (alive/age) is cleared; every other field retains
    // its process-local value until its slot is allocated again.
    for(auto& p:pyros_){p.alive=0;p.age=0;}
    emit(Kind::measure,2,0);
    const auto value=measure_ ? measure_() : std::nullopt;
    if(value && *value<2)measure_wait_=true;else logo_ready();
}
void Scene::logo_ready() {
    tone_=100;palette_show();
    for(unsigned i=0;i<4;++i) {
        emit(Kind::super_load,int(i),0,0,text(fireworks[i]));
        if(!assets_.fireworks[i].empty()) {
            const sprite::Sheet sheet(assets_.fireworks[i]);if(sheet.has_palette())palette_=sheet.palette();
        }
    }
    page_=0;emit(Kind::access,1);emit(Kind::show,0);emit(Kind::reset);queue([this]{run_logo_frame();});
}
void Scene::spawn(int y,int x,unsigned count,unsigned pattern) {
    unsigned allocated=0;
    for(auto& p:pyros_)if(!p.alive) {
        p.alive=1;p.age=0;p.origin={motion::wrap(y*16),motion::wrap(x*16)};
        p.previous_distance=p.distance=0;p.speed=std::int16_t(random_.next15()%224+64);
        p.angle=std::uint8_t(random_.next15());p.pattern=std::uint8_t(pattern);
        if(++allocated>=count)break;
    }
}
void Scene::update_pyros() {
    for(auto& p:pyros_)if(p.alive==1) {
        ++p.age;const auto pattern=unsigned(p.pattern)+p.age/4;
        if(p.age>=40){p.alive=0;p.age=0;continue;}
        int x,y;
        if(p.age<16){x=p.origin.x/16-8;y=p.origin.y/16-8;}
        else {
            if(p.age==16)emit(Kind::se,15);
            p.previous_distance=p.distance;p.distance=motion::wrap(std::int32_t(p.distance)+p.speed);
            const auto delta=motion::polar(p.angle,p.distance);const int offset=p.age<32 ? 128 : 256;
            x=motion::wrap(std::int32_t(p.origin.x)+delta.x-offset)/16;
            y=motion::wrap(std::int32_t(p.origin.y)+delta.y-offset)/16;
        }
        emit(Kind::sprite,x,y,int(pattern));
    }
}
void Scene::run_logo_frame() {
    emit(Kind::sense,held_);if(held_)skip_=true;
    switch(logo_frame_) {
    case 0:spawn(180,180,20,0);break;case 16:spawn(460,220,20,10);break;
    case 24:spawn(220,160,20,0);break;case 32:spawn(380,240,20,10);break;
    case 40:case 56:spawn(200,190,20,0);break;case 44:spawn(340,200,20,10);break;
    case 48:spawn(280,170,20,0);break;case 52:spawn(380,260,20,10);break;
    case 60:spawn(440,210,20,10);break;case 64:spawn(320,200,64,0);break;
    case 68:spawn(320,200,64,10);break;default:break;
    }
    emit(Kind::restore);update_pyros();emit(Kind::reset);
    queue([this] {
        emit(Kind::access,int(page_));page_=1-page_;emit(Kind::show,int(page_));
        if(!skip_) {
            if(logo_frame_>=16 && fade_in_<100)fade_in_+=2;
            for(unsigned i=0;i<45;++i)palette_[i]=std::uint8_t(unsigned(logo_palette_[i])*fade_in_/100);
            palette_show();
        } else {
            if(!fade_out_){finish_logo();return;}
            fade_out_-=2;tone_=fade_out_;palette_show();
        }
        emit(Kind::se_update);++logo_frame_;
        if(logo_frame_<170)queue([this]{run_logo_frame();});
        else fade(false,1,[this]{finish_logo();});
    });wait(2);
}
void Scene::finish_logo() {
    emit(Kind::super_free);emit(Kind::bg_free);emit(Kind::logo_complete);queue([this]{start_title();});
}
void Scene::start_title() {
    if(!demo_)emit(Kind::command,0x100);
    tone_=0;palette_show();emit(Kind::access,1);emit(Kind::fill,15);emit(Kind::copy,0);
    for(unsigned i=0;i<6;++i)emit(Kind::load,int(i),0,0,text(slides[i]));
    apply_palette(assets_.slides[0],0);
    fade(true,4,[this]{emit(Kind::show,0);emit(Kind::access,1);page_=0;queue([this]{slide_frame();});});
}
void Scene::slide_frame() {
    if(!(slide_frame_%4) && cel_<6) {
        emit(Kind::picture,0,38,int(cel_++));emit(Kind::access,int(page_));page_=1-page_;emit(Kind::show,int(page_));
    }
    tone_=100+int(slide_frame_)*2;palette_show();
    queue([this]{if(++slide_frame_<28)queue([this]{slide_frame();});else title_flash();});wait(1);
}
void Scene::title_flash() {
    tone_=200;palette_show();emit(Kind::show,0);emit(Kind::access,0);
    for(unsigned i=0;i<6;++i)emit(Kind::free,int(i));
    if(!demo_){emit(Kind::song,0x600,0,0,text("op"));emit(Kind::command,0);}
    emit(Kind::access,1);emit(Kind::load,0,0,0,text("op1.pi"));apply_palette(assets_.menu,0);
    emit(Kind::picture);emit(Kind::free,0);emit(Kind::copy,0);
    palette_.fill(255);palette_show();tone_=100;palette_show();white_=240;fade_frame_=0;
    queue([this]{monochrome_frame();});
}
void Scene::monochrome_frame() {
    for(unsigned i=0;i<3;++i)palette_[i]=white_;
    palette_show();
    queue([this]{white_-=16;if(++fade_frame_<15)queue([this]{monochrome_frame();});
        else {white_=252;fade_frame_=0;queue([this]{color_frame();});}});wait(1);
}
void Scene::color_frame() {
    for(unsigned i=3;i<48;++i)if(assets_.menu.palette[i]<palette_[i])palette_[i]=white_;
    palette_show();queue([this]{white_-=4;if(++fade_frame_<63)queue([this]{color_frame();});
        else {apply_palette(assets_.menu,0);finished_=true;emit(Kind::complete);}});wait(1);
}
Renderer::Renderer(const Assets& assets):assets_(assets) {for(auto& page:pages_)page.resize(256000);}
void Renderer::apply(const Event& e) {
    switch(e.kind) {
    case Kind::access:accessed_=unsigned(e.a);break;
    case Kind::show:shown_=unsigned(e.a);break;
    case Kind::load:
        if(e.data==text("zun00.pi"))loaded_.at(unsigned(e.a))=&assets_.logo;
        else if(e.data==text("op1.pi"))loaded_.at(unsigned(e.a))=&assets_.menu;
        else {auto at=std::find_if(std::begin(slides),std::end(slides),[&](const char* name){return e.data==text(name);});
            if(at==std::end(slides))throw std::invalid_argument("startup PI resource");
            loaded_.at(unsigned(e.a))=&assets_.slides[unsigned(at-std::begin(slides))];}break;
    case Kind::free:loaded_.at(unsigned(e.a))=nullptr;break;
    case Kind::picture: {
        const auto* image=loaded_.at(unsigned(e.c));if(!image || image->pixels.size()!=std::size_t(image->width)*image->height/2)
            throw std::logic_error("startup PI slot");
        const int left=(e.a/8)*8;
        for(unsigned y=0;y<image->height;++y)for(unsigned x=0;x<image->width;++x) {
            const int px=left+int(x),py=(e.b+int(y))%400;
            if(px<0 || px>=640 || py<0)continue;
            const auto value=image->pixels[(std::size_t(y)*image->width+x)/2];
            pages_[accessed_][unsigned(py)*640+unsigned(px)]=std::uint8_t((x&1) ? value&15 : value>>4);
        }break;
    }
    case Kind::copy:accessed_=unsigned(e.a);pages_[accessed_]=pages_[1-accessed_];break;
    case Kind::clear:std::fill(pages_[accessed_].begin(),pages_[accessed_].end(),0);break;
    case Kind::fill:std::fill(pages_[accessed_].begin(),pages_[accessed_].end(),std::uint8_t(e.a));break;
    case Kind::snap:background_=pages_[accessed_];break;
    case Kind::restore:if(background_.size()!=256000)throw std::logic_error("startup background absent");pages_[accessed_]=background_;break;
    case Kind::bg_free:background_.clear();break;
    case Kind::super_load:sheets_.push_back(std::make_unique<sprite::Sheet>(assets_.fireworks.at(unsigned(e.a))));break;
    case Kind::super_free:sheets_.clear();break;
    case Kind::sprite: {
        unsigned pattern=unsigned(e.c);const sprite::Sheet* sheet=nullptr;
        for(const auto& part:sheets_) {if(pattern<part->count()){sheet=part.get();break;}pattern-=part->count();}
        if(!sheet)throw std::out_of_range("startup fireworks pattern");
        for(unsigned y=0;y<sheet->height();++y)for(unsigned x=0;x<sheet->width();++x) {
            const int px=e.a+int(x),py=e.b+int(y);const auto color=sheet->pixel(pattern,x,y);
            if(color && px>=0 && px<640 && py>=0 && py<400)pages_[accessed_][unsigned(py)*640+unsigned(px)]=color;
        }break;
    }
    case Kind::palette_show: {
        if(e.data.size()!=48)throw std::invalid_argument("startup RGB palette");
        const unsigned tone=unsigned(std::clamp(e.a,0,200)),scale=tone>100 ? 200-tone : tone;
        const unsigned invert=tone>100 ? 15 : 0;
        for(unsigned i=0;i<48;++i)dac_[i]=std::uint8_t((((e.data[i]>>4)^invert)*scale/100)^invert);
        break;
    }
    default:break;
    }
}
Bytes Renderer::rgb() const {
    Bytes result;result.reserve(768000);
    for(auto index:pages_[shown_])for(unsigned component=0;component<3;++component)result.push_back(std::uint8_t(dac_[unsigned(index)*3+component]*17));
    return result;
}
}

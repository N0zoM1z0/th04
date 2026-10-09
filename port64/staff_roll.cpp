#include "staff_roll.hpp"
#include "cdg_image.hpp"
#include "motion.hpp"
#include <algorithm>
#include <stdexcept>

namespace th04::portable::staff {
void Script::emit(Kind k,int a,int b,int c,int d,std::string name) {
    events_.emplace_back(k,a,b,c,d,std::move(name));
}
void Script::load(unsigned slot,unsigned number,const Lookup& lookup) {
    const std::string base="SFF"+std::to_string(number);
    emit(Kind::cdg_load,int(slot),0,0,0,base+".CDG");
    slots_.at(slot)=lookup(base+".CDG");
    emit(Kind::cdg_load,int(slot+1),1,0,0,base+"B.CDG");
    slots_.at(slot+1)=lookup(base+"B.CDG");
}
void Script::restore(int x,int y,unsigned slot,int distance) {
    const int half=distance/2;
    const auto size=slots_.at(slot);
    if(!size.width || !size.height) throw std::logic_error("Staff Roll restore slot is empty");
    emit(Kind::bg_rect,x-half,y-half,int(size.width)+half*2,int(size.height)+half*2);
}
void Script::draw(int x,int y,int distance) {
    if(!distance) { emit(Kind::cdg_put,x,y,int(slot_));return; }
    emit(Kind::grcg_on);
    // Original polar multiplies signed words into a signed DWORD and SARs
    // by eight: negative displacement rounds down, not toward zero.
    const auto position=[&](std::uint8_t angle,int radius) {
        return motion::polar(angle,static_cast<motion::Subpixel>(radius));
    };
    for(unsigned plane=0;plane<4;++plane) {
        motion::Point offset{};
        if(shape_==Shape::radial) {
            offset=position(angle_,distance/4);
            angle_=static_cast<std::uint8_t>(angle_+64);
        } else if(shape_==Shape::diagonal) {
            const int half=distance/2;
            if(plane==0) { offset.x=position(96,half/2).x;offset.y=position(32,half/2).x; }
            if(plane==1) { offset.x=position(64,half).x;offset.y=position(0,half).x; }
            if(plane==2) { offset.x=position(224,half/2).x;offset.y=position(160,half/2).x; }
            if(plane==3) { offset.x=position(192,half).x;offset.y=position(128,half).x; }
        } else {
            const int half=distance/2;
            // Plane2/3's Y coordinate intentionally uses cosine64 (zero).
            // This is an axis dissolve, even though the source looks polar.
            const auto radius=(plane&1) ? half : half/2;
            offset.x=position(plane<2 ? 0 : 128,radius).x;
        }
        emit(Kind::plane,x+offset.x,y+offset.y,int(slot_+1),int(plane));
    }
    emit(Kind::grcg_off);
}
void Script::dissolve(int x,int y,bool out) {
    int distance=out ? 63 : 0;unsigned page=0;
    emit(Kind::access,0);emit(Kind::show,1);
    for(;;) {
        restore(x,y,slot_,out ? distance+1 : distance);
        distance+=out ? -1 : 1;
        angle_=static_cast<std::uint8_t>(angle_+8);
        if(!out && distance>=64) break;
        draw(x,y,distance);emit(Kind::vsync,2);
        emit(Kind::show,int(page));page=1-page;emit(Kind::access,int(page));
        if(out && distance<=0) break;
    }
    // graph_copy_page's argument is the destination. It copies from the
    // opposite hardware page and leaves access on the destination, regardless
    // of which page the preceding draw selected.
    emit(Kind::copy_page,int(out ? page : 1-page));
}
void Script::two(int x1,int y1,int x2,int y2) {
    unsigned page=0;emit(Kind::access,0);emit(Kind::show,1);
    for(int distance=0;;) {
        restore(x1,y1,2,distance);restore(x2,y2,0,distance);
        ++distance;angle_=static_cast<std::uint8_t>(angle_-8);
        if(distance>=64) break;
        slot_=2;draw(x1,y1,distance);slot_=0;draw(x2,y2,distance);
        emit(Kind::vsync,2);emit(Kind::show,int(page));page=1-page;emit(Kind::access,int(page));
    }
    emit(Kind::copy_page,int(1-page));
}
Script::Script(const Lookup& lookup,std::uint8_t angle):angle_(angle) {
    const auto background=[&](unsigned number) {
        emit(Kind::access,1);emit(Kind::pi_load,0,0,0,0,"SFF"+std::to_string(number)+".PI");
        emit(Kind::pi_palette);emit(Kind::pi_put);emit(Kind::pi_free);
        emit(Kind::copy_page,0);emit(Kind::snap);
    };
    const auto wait=[&](int measure,int fallback=160) { emit(Kind::measure,measure,fallback); };
    emit(Kind::tone,0);background(1);
    emit(Kind::bgm_control,0x100);emit(Kind::bgm_load,0x600,0,0,0,"STAFF");emit(Kind::bgm_control,0);
    emit(Kind::fade,1,12);load(0,1,lookup);
    wait(3,64);slot_=0;shape_=Shape::radial;dissolve(352,160,true);load(2,2,lookup);
    wait(7);shape_=Shape::diagonal;dissolve(352,160,false);
    slot_=2;shape_=Shape::axis;dissolve(192,128,true);
    emit(Kind::access,0);slot_=0;load(0,3,lookup);
    wait(11);dissolve(288,200,true);
    wait(19);shape_=Shape::diagonal;two(192,128,288,200);
    emit(Kind::fade,0,4);emit(Kind::cdg_free_all);background(2);emit(Kind::fade,1,4);load(2,4,lookup);
    wait(23);slot_=2;shape_=Shape::axis;dissolve(32,112,true);
    emit(Kind::cdg_free,2);load(4,5,lookup);
    wait(27);slot_=4;shape_=Shape::diagonal;dissolve(32,184,true);load(0,8,lookup);
    wait(31);shape_=Shape::axis;dissolve(32,184,false);slot_=0;dissolve(64,184,true);load(4,9,lookup);
    wait(35);shape_=Shape::radial;dissolve(64,184,false);slot_=4;dissolve(64,184,true);load(0,6,lookup);
    wait(39);shape_=Shape::diagonal;dissolve(64,184,false);slot_=0;dissolve(32,184,true);
    wait(43);shape_=Shape::axis;two(32,112,32,184);load(0,7,lookup);slot_=0;dissolve(32,336,true);
    wait(48);emit(Kind::bg_free);emit(Kind::cdg_free_all);emit(Kind::fade,0,4);
}
const char* kind_name(Kind k) {
    static const char* names[]={"tone","access","show","pi_load","pi_palette","pi_put","pi_free","copy_page",
        "snap","bg_free","bgm_control","bgm_load","fade","cdg_load","cdg_free","cdg_free_all","measure",
        "bg_rect","cdg_put","plane","grcg_on","grcg_off","vsync"};
    return names[static_cast<unsigned>(k)];
}
Scene::Scene(const Assets& assets,std::array<Bytes,2> pages,unsigned shown)
    :assets_(&assets),script_([&](const std::string& name) {
        const CdgSheet sheet(assets.sprites.at(name));return Dimensions{sheet.width,sheet.height};
    }),pages_(std::move(pages)),shown_(shown&1) {
    for(auto& page:pages_) {
        if(page.empty())page.resize(640*400);
        if(page.size()!=640*400)throw std::invalid_argument("Staff Roll needs two complete graphics pages");
    }
}
unsigned Scene::live_slots() const {
    return static_cast<unsigned>(std::count_if(slots_.begin(),slots_.end(),[](const Bytes* p) { return p!=nullptr; }));
}
void Scene::apply(const Event& e) {
    switch(e.kind) {
    case Kind::tone:tone_=e.a;break;
    case Kind::access:access_=unsigned(e.a)&1;break;
    case Kind::show:shown_=unsigned(e.a)&1;break;
    case Kind::pi_load:loaded_=&assets_->pictures.at(e.name);break;
    case Kind::pi_palette:
        if(!loaded_)throw std::logic_error("Staff Roll PI palette slot is empty");
        palette_=loaded_->palette;break;
    case Kind::pi_put:
        if(!loaded_ || loaded_->width!=640 || loaded_->height!=400 || loaded_->pixels.size()!=128000)
            throw std::invalid_argument("Staff Roll background must be a complete 640x400 PI");
        for(unsigned i=0;i<640*400;++i)pages_[access_][i]=std::uint8_t((i&1) ? loaded_->pixels[i/2]&15 : loaded_->pixels[i/2]>>4);
        break;
    case Kind::pi_free:loaded_=nullptr;break;
    case Kind::copy_page:access_=unsigned(e.a)&1;pages_[access_]=pages_[1-access_];break;
    case Kind::snap:background_=pages_[access_];break;
    case Kind::bg_free:background_.clear();break;
    case Kind::cdg_load:slots_.at(unsigned(e.a))=&assets_->sprites.at(e.name);break;
    case Kind::cdg_free:slots_.at(unsigned(e.a))=nullptr;break;
    case Kind::cdg_free_all:slots_.fill(nullptr);break;
    case Kind::bg_rect: {
        if(background_.size()!=640*400)throw std::logic_error("Staff Roll background snapshot is empty");
        // BGIMAGER's TH04 JNS loop copies h+1 rows. X starts on a WORD;
        // the right extent follows its SHR/conditional increment, not a
        // generic clipped-pixel rectangle API.
        const int left=e.a&~15;
        const int offset=e.a&15;
        const int width=((offset+e.c)/16+(offset ? 1 : 0))*16;
        for(int y=0;y<=e.d;++y) for(int x=0;x<width;++x) {
            const int at=(e.b+y)*640+left+x;
            if(at>=0 && at<640*400)pages_[access_][unsigned(at)]=background_[unsigned(at)];
        }
        break;
    }
    case Kind::cdg_put:case Kind::plane: {
        const auto* bytes=slots_.at(unsigned(e.c));
        if(!bytes)throw std::logic_error("Staff Roll draw slot is empty");
        const CdgSheet sheet(*bytes);
        const bool combined=sheet.layout==CdgSheet::alpha_and_colors;
        if(e.kind==Kind::cdg_put && !combined)throw std::invalid_argument("Staff Roll opaque draw needs an alpha/color slot");
        if(sheet.layout==CdgSheet::alpha_only)throw std::invalid_argument("Staff Roll plane draw needs color planes");
        const int left=e.kind==Kind::cdg_put ? e.a&~7 : e.a;
        for(unsigned y=0;y<sheet.height;++y) for(unsigned x=0;x<sheet.width;++x) {
            const int at=(e.b+int(y))*640+left+int(x);
            if(at<0 || at>=640*400)continue;
            auto& pixel=pages_[access_][unsigned(at)];
            if(e.kind==Kind::plane) {
                if(sheet.bit(0,unsigned(e.d)+(combined ? 1 : 0),x,y))pixel=15;
            } else {
                if(sheet.bit(0,0,x,y))pixel=0;
                for(unsigned plane=0;plane<4;++plane)if(sheet.bit(0,plane+1,x,y))pixel|=std::uint8_t(1u<<plane);
            }
        }
        break;
    }
    case Kind::bgm_control:case Kind::bgm_load:case Kind::measure:sound_.push_back(e);break;
    case Kind::fade:case Kind::grcg_on:case Kind::grcg_off:case Kind::vsync:break;
    }
}
void Scene::advance(const Sink& observer) {
    if(status_==Status::stopped)return;
    ++clock_;
    if(status_==Status::measure) {
        if(measure_source_)measure_=measure_source_();
        if(!measure_ || *measure_<measure_goal_)return;
        status_=Status::running;
    }
    if(status_==Status::delay) {
        if(left_>0 && --left_>0)return;
        if(fade_step_) {
            tone_+=fade_step_;
            if((fade_step_>0 && tone_>=fade_goal_) || (fade_step_<0 && tone_<=fade_goal_)) {
                tone_=fade_goal_;fade_step_=0;
            } else {left_=fade_speed_;return;}
        }
        status_=Status::running;
    }
    while(next_<script_.requests().size()) {
        const auto& e=script_.requests()[next_++];apply(e);
        if(e.kind==Kind::fade) {
            tone_=e.a ? 0 : 100;fade_goal_=e.a ? 100 : 0;fade_step_=e.a ? 6 : -6;
            fade_speed_=e.b;left_=1+e.b;status_=Status::delay;
        } else if(e.kind==Kind::vsync) {left_=e.a;status_=Status::delay;}
        else if(e.kind==Kind::measure) {
            if(measure_source_)measure_=measure_source_();
            if(audio_active_ && (!measure_ || *measure_<std::uint16_t(e.a))) {
                measure_goal_=std::uint16_t(e.a);status_=Status::measure;
            } else if(!audio_active_ && e.b) {left_=e.b;status_=Status::delay;}
        }
        if(observer)observer(e);
        if(status_!=Status::running)return;
    }
    status_=Status::stopped;
}
} // namespace th04::portable::staff

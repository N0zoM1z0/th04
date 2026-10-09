#include "op_setup.hpp"
#include <algorithm>
#include <stdexcept>

namespace th04::portable::op_setup {
namespace {Bytes bytes(const std::string& s) {return {s.begin(),s.end()};}}
#include "op_setup_text.inl"
const char* kind_name(Kind k) {
    constexpr const char* names[]={"tone","super_load","access","load","palette","picture","free","copy","vsync",
        "sprite","rectangle","text","reset","delay","sense","option","super_free"};
    return names[unsigned(k)];
}
Scene::Scene(Sink sink,unsigned effect):sink_(std::move(sink)),effect_(effect) {
    if(effect>7)throw std::invalid_argument("setup text effect");
    emit(Kind::tone,0);emit(Kind::super_load,0,0,0,0,bytes("mswin.bft"));
    emit(Kind::access,1);emit(Kind::load,0,0,0,0,bytes("ms.pi"));
    emit(Kind::palette);emit(Kind::picture);emit(Kind::free);emit(Kind::copy,0);
    fade(true);queue([this]{begin_submenu(0);});drain();
}
void Scene::emit(Kind kind,int a,int b,int c,int d,Bytes data) {
    if(kind==Kind::tone)tone_=a;
    if(sink_)sink_({kind,tick_,a,b,c,d,std::move(data)});
}
void Scene::queue(std::function<void()> f) {tasks_.push_back(std::move(f));}
void Scene::drain() {
    while(!waiting_ && phase_==Phase::tasks && !tasks_.empty()) {
        auto f=std::move(tasks_.front());tasks_.pop_front();f();
    }
}
void Scene::wait(Kind kind) {emit(kind,kind==Kind::delay ? 1 : 0);waiting_=1;}
void Scene::fade(bool in) {
    for(unsigned i=0;i<18;++i) {
        queue([this]{wait(Kind::vsync);});
        queue([this,in,i]{emit(Kind::tone,in ? std::min(100,int(i)*6) : std::max(0,100-int(i)*6));});
    }
}
void Scene::singleline(int left,int top,unsigned width) {
    queue([this,width]{width_=width;});
    queue([this,left,top,width]{
        emit(Kind::rectangle,left,top,int(width)*16,32);
        for(unsigned x=0;x<width;++x) {
            const int xx=left+int(x)*16;
            emit(Kind::sprite,xx,top,x==0 ? 5 : x+1==width ? 8 : 1);
            emit(Kind::sprite,xx,top+16,x==0 ? 6 : x+1==width ? 7 : 3);
        }
    });
}
void Scene::dropdown(int left,int top,unsigned width,unsigned height) {
    queue([this,width,height]{width_=width;height_=height;});
    queue([this,left,top,width]{for(unsigned x=0;x<width;++x)
        emit(Kind::sprite,left+int(x)*16,top,x==0 ? 5 : x+1==width ? 8 : 1);});
    for(unsigned i=1;i<height*2-3;++i) {
        queue([this,left,top,width,i]{
            const int y=top+16+int(i-1)*8;emit(Kind::rectangle,left,y,int(width)*16,16);
            for(unsigned x=0;x<width;++x) {
                const int xx=left+int(x)*16;
                emit(Kind::sprite,xx,y,x==0 ? 2 : x+1==width ? 4 : 0);
                emit(Kind::sprite,xx,y+8,x==0 ? 6 : x+1==width ? 7 : 3);
            }
        });queue([this]{wait(Kind::delay);});
    }
}
void Scene::rollup(int left,int top,unsigned width,unsigned height) {
    queue([this,width,height]{width_=width;height_=height;});
    for(unsigned i=1;i<height*2-2;++i) {
        queue([this,left,top,width,height,i]{
            const int y=top+int(height-1)*16-int(i-1)*8;
            emit(Kind::rectangle,left,y+8,int(width)*16,16);
            for(unsigned x=0;x<width;++x)emit(Kind::sprite,left+int(x)*16,y,x==0 ? 6 : x+1==width ? 7 : 3);
        });queue([this]{wait(Kind::delay);});
    }
}
void Scene::choice(unsigned mode,unsigned color) {
    const unsigned row=submenu_ ? (mode==1 ? 0 : mode==2 ? 1 : 2) : 2-mode;
    emit(Kind::text,48,136+int(row)*16,int(color),int(effect_),bytes(texts().choices[submenu_][mode]));
}
void Scene::begin_submenu(unsigned menu) {
    submenu_=menu;selection_=menu ? 1 : 2;
    singleline(96,80,28);
    queue([this]{emit(Kind::text,112,88,15,int(effect_),bytes(texts().captions[submenu_]));});
    dropdown(32,128,10,4);
    queue([this]{for(unsigned i=0;i<3;++i)choice(i,i==selection_ ? 15 : 0);});
    dropdown(192,128,25,10);
    queue([this]{for(unsigned i=0;i<9;++i)emit(Kind::text,208,136+int(i)*16,15,int(effect_),bytes(texts().help[submenu_][i]));});
    queue([this]{release();});
}
void Scene::input_wait(Phase phase) {
    phase_=phase;latch_=before_;emit(Kind::reset,before_);wait(Kind::delay);
}
void Scene::release() {input_wait(Phase::release);}
void Scene::controls() {
    if(latch_&0x2020) {
        phase_=Phase::tasks;rollup(192,128,25,10);rollup(32,128,10,4);
        queue([this]{
            if(!submenu_)bgm_=selection_;else se_=selection_;
            emit(Kind::option,int(submenu_),int(selection_));
        });
        if(!submenu_) {
            queue([this]{wait(Kind::delay);});queue([this]{emit(Kind::copy,0);begin_submenu(1);});
        } else {
            fade(false);queue([this]{emit(Kind::super_free);phase_=Phase::stopped;});
        }
        drain();return;
    }
    const unsigned inc=submenu_ ? 2 : 1,dec=submenu_ ? 1 : 2;
    if(latch_&inc) {choice(selection_,0);selection_=(selection_+1)%3;choice(selection_,15);}
    if(latch_&dec) {choice(selection_,0);selection_=(selection_+2)%3;choice(selection_,15);}
    release();
}
void Scene::advance(std::uint16_t before,std::uint16_t after) {
    if(finished())return;
    before_=before;after_=after;++tick_;
    if(!waiting_)throw std::logic_error("setup has no refresh wait");
    --waiting_;
    switch(phase_) {
    case Phase::release:case Phase::press: {
        latch_|=after_;emit(Kind::sense,after_);
        if(phase_==Phase::release)input_wait(latch_ ? Phase::release : Phase::press);
        else if(!latch_)input_wait(Phase::press);
        else {phase_=Phase::post_press;wait(Kind::delay);}
        break;
    }
    case Phase::post_press:controls();break;
    case Phase::tasks:drain();break;
    case Phase::stopped:break;
    }
}
Renderer::Renderer(const Assets& assets):canvas_(assets.graphics),assets_(assets) {}
void Renderer::apply(const Event& e) {
    using K=cutscene::Kind;
    switch(e.kind) {
    case Kind::super_load:windows_=std::make_unique<sprite::Sheet>(assets_.windows);break;
    case Kind::super_free:windows_.reset();break;
    case Kind::access:canvas_.apply({K::access,e.a});break;
    case Kind::load: {cutscene::Event load(K::pi_load);load.name={e.data.begin(),e.data.end()};canvas_.apply(load);break;}
    case Kind::palette:canvas_.apply({K::pi_palette});break;
    case Kind::picture:canvas_.apply({K::pi_put});break;
    case Kind::free:canvas_.apply({K::pi_free});break;
    case Kind::copy:canvas_.apply({K::copy_page,e.a});break;
    case Kind::rectangle:canvas_.copy_rectangle(1,0,e.a,e.b,unsigned(e.c),unsigned(e.d));break;
    case Kind::text:canvas_.put_text(e.a,e.b,{e.data.begin(),e.data.end()},unsigned(e.c),unsigned(e.d));break;
    case Kind::sprite: {
        if(!windows_ || e.c<0 || unsigned(e.c)>=windows_->count())throw std::invalid_argument("setup window pattern");
        auto& page=canvas_.drawing_page();
        for(unsigned y=0;y<windows_->height();++y)for(unsigned x=0;x<windows_->width();++x) {
            const int px=e.a+int(x),py=e.b+int(y);const auto color=windows_->pixel(unsigned(e.c),x,y);
            if(color && px>=0 && px<640 && py>=0 && py<400)page[unsigned(py)*640+unsigned(px)]=color;
        }break;
    }
    default:break;
    }
}
Bytes Renderer::rgb(int tone) const {
    Bytes result;result.reserve(640*400*3);const auto& pal=canvas_.palette();
    for(auto index:canvas_.page(canvas_.shown_page()))for(unsigned component=0;component<3;++component)
        result.push_back(std::uint8_t((pal[unsigned(index)*3+component]>>4)*unsigned(std::clamp(tone,0,100))/100*17));
    return result;
}
}

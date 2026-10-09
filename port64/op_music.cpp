#include "op_music.hpp"
#include <algorithm>
#include <stdexcept>

namespace th04::portable::op_music {
namespace {
Bytes bytes(const std::string& s) {return Bytes(s.begin(),s.end());}
int floor16(std::int64_t x) {return int(x>=0 ? x/65536 : -((-x+65535)/65536));}
int pixel_y(int y) {return y>=0 ? y/16 : -((-y+15)/16);}
void velocity(Polygon& p,int x) {p.velocity.x=motion::wrap(x ? x : 1);}
void angles(Polygon& p,const score_file::Random& random) {
    p.velocity.y=motion::wrap(32+((random()&3)<<4));
    p.angle=Byte(random());p.angle_speed=Byte(4-int(random()&7));
    if(!p.angle_speed)p.angle_speed=4;
}
}
const char* kind_name(Kind k) {
    constexpr const char* names[]={"cdg_free","text_clear","tone","show","access","clear","load","palette","picture","free","copy",
        "background_snap","background_rect","background_free","blue_snap","blue_restore","blue_free","grcg","text","polygon","delay","poll","sound","song","file","fade","vsync"};
    return names[unsigned(k)];
}
void update_polygons(State& s,const score_file::Random& random,const std::function<void(const std::vector<Point>&)>& draw) {
    if(!s.initialized) {
        for(auto& p:s.polygons) {
            // Original calls X, Y, Vx, Vy, angle, angular speed in this order.
            p.center.x=motion::wrap(random()%640);p.center.y=motion::wrap(random()%6400);
            velocity(p,4-int(random()&7));angles(p,random);
        }
        s.initialized=true;
    }
    for(unsigned i=0;i<s.polygons.size();++i) {
        auto& p=s.polygons[i];const unsigned count=3+i/4;std::vector<Point> points;
        for(unsigned v=0;v<count;++v) {
            const auto delta=motion::polar(Byte(v*256/count+p.angle),motion::wrap(64+(i&3)*16));
            points.push_back({motion::wrap(int(p.center.x)+delta.x),motion::wrap(pixel_y(p.center.y)+delta.y)});
        }
        points.push_back(points.front());
        p.center.x=motion::wrap(int(p.center.x)+p.velocity.x);p.center.y=motion::wrap(int(p.center.y)+p.velocity.y);
        p.angle=Byte(p.angle+p.angle_speed);
        if(p.center.x<=0 || p.center.x>=639)p.velocity.x=motion::wrap(-int(p.velocity.x));
        if(p.center.y>=8000) {
            p.center.x=motion::wrap(random()%640);p.center.y=-1600;
            velocity(p,8-int(random()&15));angles(p,random);
        }
        draw(points); // The original renders vertices built before movement/reset.
    }
}
void paint_polygon(Bytes& page,const std::vector<Point>& input) {
    if(page.size()!=256000 || input.size()<4)throw std::invalid_argument("Music polygon geometry");
    const unsigned n=unsigned(input.size()-1);
    if(input.back().x!=input.front().x || input.back().y!=input.front().y)throw std::invalid_argument("Music polygon closure");
    int ymin=input[0].y,ymax=ymin,xmin=input[0].x,xmax=xmin;unsigned left=0,right=0;
    for(unsigned i=1;i<n;++i) {
        if(input[i].y<ymin) {ymin=input[i].y;left=right=i;}
        else if(input[i].y==ymin)right=i;
        ymax=std::max(ymax,int(input[i].y));xmin=std::min(xmin,int(input[i].x));xmax=std::max(xmax,int(input[i].x));
    }
    if(ymin>399 || ymax<0 || xmin>639 || xmax<0)return;
    if(left==0 && right==n-1)std::swap(left,right);
    struct Edge {unsigned end;int direction;std::int64_t x,step;};
    const auto next=[&](unsigned i,int direction){return unsigned((int(i)+direction+int(n))%int(n));};
    const auto setup=[&](Edge& e,unsigned start,bool clip) {
        unsigned end=next(start,e.direction);unsigned guard=0;
        if(clip)while(input[end].y<0) {start=end;end=next(end,e.direction);if(++guard>n)throw std::logic_error("Music polygon edge");}
        const Point a=input[start],b=input[end];int x=a.x,y=a.y;
        if(clip && y<0) {x+=int(std::int64_t(int(b.x)-a.x)*(-y)/(int(b.y)-y));y=0;}
        const int height=int(b.y)-y;
        e.end=end;e.x=std::int64_t(x)*65536+32768;
        // make_linework truncates the signed fixed-point quotient towards zero.
        e.step=std::int64_t(motion::wrap(int(b.x)-x))*65536/(height ? height : 1);
    };
    Edge a{left,-1,0,0},b{right,1,0,0};setup(a,left,true);setup(b,right,true);
    int y=std::max(ymin,0),bottom=std::min(ymax,399);unsigned guard=0;
    while(y<=bottom) {
        if(++guard>n*2+1)throw std::invalid_argument("Music polygon is not convex");
        const int end=std::min(int(input[a.end].y),int(input[b.end].y));
        const bool final=bottom<=end;const int last=final ? bottom : end-1;
        // draw_trapezoid writes once even with length -1 at a zero-height edge.
        for(int row=y;row<=std::max(y,last);++row) {
            const int xa=floor16(a.x),xb=floor16(b.x),lo=std::max(0,std::min(xa,xb)),hi=std::min(639,std::max(xa,xb));
            if(row>=0 && row<400)for(int x=lo;x<=hi;++x)page[unsigned(row)*640+unsigned(x)]|=1;
            a.x+=a.step;b.x+=b.step;
        }
        if(final)break;
        y=end;
        if(input[a.end].y==end)setup(a,a.end,false);
        if(input[b.end].y==end)setup(b,b.end,false);
    }
}
Scene::Scene(State& s,const Assets& assets,score_file::Random random,Sink sink)
    :state_(s),assets_(assets),random_(std::move(random)),sink_(std::move(sink)) {
    if(s.playing>=22 || assets.comments.size()<22*800)throw std::invalid_argument("Music Room track/comments");
    s.comment_shown=0;s.page=1;
    emit(Kind::cdg_free);emit(Kind::text_clear);emit(Kind::tone,0);emit(Kind::show,0);access(0);emit(Kind::clear);
    access(1);emit(Kind::load,0,0,0,0,bytes("music.pi"));emit(Kind::palette);emit(Kind::picture);emit(Kind::free);
    s.selected=s.playing;for(unsigned i=0;i<24;++i)track(i,i==s.selected ? 3 : 5);
    emit(Kind::copy,0);emit(Kind::background_snap);access(1);emit(Kind::show,0);emit(Kind::blue_snap);
    transition(s.playing);
    queue([this]{tone_=100;emit(Kind::tone,100);phase_=Phase::entry_release;});
    drain(0);
}
void Scene::emit(Kind kind,int a,int b,int c,int d,Bytes data) {
    if(sink_)sink_({kind,ticks_,a,b,c,d,std::move(data)});
}
void Scene::access(int page) {emit(Kind::access,page);}
void Scene::track(unsigned i,unsigned color) {
    for(unsigned page:{1u-state_.page,unsigned(state_.page)}) {
        access(int(page));emit(Kind::text,16,8+int(i)*16,int(color),int(state_.text_effect),bytes(titles().at(i)));
    }
}
void Scene::comment_load(unsigned track) {
    const auto at=track*800;
    emit(Kind::file,0,0,0,0,bytes("_MUSIC.TXT"));emit(Kind::file,1,int(at));
    std::copy_n(assets_.comments.begin()+at,800,state_.comment.begin());
    emit(Kind::file,2,800,0,0,Bytes(state_.comment.begin(),state_.comment.end()));emit(Kind::file,3);
    for(unsigned line=0;line<20;++line)state_.comment[line*40+38]=0;
}
void Scene::comment() {
    for(unsigned line=0;line<20;++line) {
        const auto start=state_.comment.begin()+line*40;
        if(line && *start==';')continue;
        const auto end=std::find(start,start+40,Byte(0));
        emit(Kind::text,320,int(line+4)*16,7,int(state_.text_effect),Bytes(start,end));
    }
}
void Scene::animate() {
    emit(Kind::blue_restore);emit(Kind::grcg,0xce,15);
    update_polygons(state_,random_,[this](const std::vector<Point>& points) {
        Bytes packed;for(const auto& p:points)for(int value:{int(p.x),int(p.y)}) {packed.push_back(Byte(value));packed.push_back(Byte(unsigned(value)>>8));}
        emit(Kind::polygon,int(points.size()-1),0,0,0,std::move(packed));
    });
    emit(Kind::grcg,0);emit(Kind::show,state_.page);state_.page=Byte(1-state_.page);access(state_.page);
    emit(Kind::delay,1);waiting_=true;
}
void Scene::queue(std::function<void()> f) {tasks_.push_back(std::move(f));}
void Scene::transition(unsigned track) {
    if(state_.comment_shown) {
        queue([this]{state_.text_effect=2;emit(Kind::background_rect,320,64,320,320);animate();});
        queue([this]{emit(Kind::background_rect,320,64,320,320);});
    }
    queue([this,track]{comment_load(track);emit(Kind::blue_restore);emit(Kind::background_rect,320,64,320,320);});
    if(state_.comment_shown) {
        for(unsigned effect=4;effect<8;++effect)for(unsigned page=0;page<2;++page)
            queue([this,effect]{state_.text_effect=effect;comment();animate();});
        queue([this]{state_.text_effect=2;comment();animate();});queue([this]{comment();});
    } else {
        queue([this]{state_.comment_shown=1;comment();animate();});queue([this]{comment();});
    }
    queue([this]{emit(Kind::blue_restore);});
}
void Scene::controls(std::uint16_t held) {
    sampled_=held;emit(Kind::poll,held);
    if(held&1) {track(state_.selected,5);state_.selected=Byte(state_.selected ? state_.selected-1 : 23);if(state_.selected==22)--state_.selected;track(state_.selected,3);}
    if(held&2) {track(state_.selected,5);state_.selected=Byte(state_.selected<23 ? state_.selected+1 : 0);if(state_.selected==22)++state_.selected;track(state_.selected,3);}
    if(held&0x2020) {
        if(state_.selected==23) {phase_=Phase::release;return;}
        emit(Kind::sound,0x220);state_.playing=state_.selected;transition(state_.playing);
        queue([this]{emit(Kind::song,0x600,0,0,0,bytes(songs()[state_.playing]));emit(Kind::sound,0);finish_controls();});
    } else finish_controls();
}
void Scene::finish_controls() {
    if(sampled_&0x1000)phase_=Phase::release;
    else if(!sampled_) {phase_=Phase::controls;animate();}
    else phase_=Phase::entry_release;
}
void Scene::fade() {
    ++fade_ticks_;tone_=fade_ticks_==18 ? 0 : 100-int(fade_ticks_-1)*6;emit(Kind::tone,tone_);
    if(fade_ticks_==18) {
        emit(Kind::background_free);emit(Kind::song,0x600,0,0,0,bytes("op"));emit(Kind::sound,0);
        stopped_=true;phase_=Phase::stopped;
    } else {emit(Kind::vsync);queue([this]{fade();});waiting_=true;}
}
void Scene::drain(std::uint16_t held) {
    while(!waiting_ && !stopped_) {
        if(!tasks_.empty()) {auto f=std::move(tasks_.front());tasks_.pop_front();f();continue;}
        switch(phase_) {
        case Phase::entry_release:
            emit(Kind::poll,held);if(held)animate();else phase_=Phase::controls;break;
        case Phase::controls:controls(held);break;
        case Phase::release:
            emit(Kind::poll,held);
            if(held)animate();else {
                emit(Kind::sound,0x210);emit(Kind::blue_free);emit(Kind::show,0);access(0);
                phase_=Phase::fade;fade_ticks_=0;emit(Kind::fade,1,1);emit(Kind::vsync);queue([this]{fade();});waiting_=true;
            }
            break;
        default:throw std::logic_error("Music Room queued phase");
        }
    }
}
void Scene::advance(std::uint16_t held) {
    if(stopped_)return;
    ++ticks_;waiting_=false;drain(held);
}
Renderer::Renderer(const Assets& assets,std::array<Bytes,2> pages,unsigned shown):canvas_(assets.graphics,std::move(pages),shown) {}
void Renderer::apply(const Event& e) {
    using K=cutscene::Kind;
    switch(e.kind) {
    case Kind::text:canvas_.put_text(e.a,e.b,std::string(e.data.begin(),e.data.end()),unsigned(e.c),unsigned(e.d));break;
    case Kind::blue_snap:
        blue_=canvas_.drawing_page();for(auto& pixel:blue_)pixel&=1;break;
    case Kind::blue_restore: {
        auto& p=canvas_.drawing_page();if(blue_.size()!=p.size())throw std::logic_error("Music blue plane missing");
        for(unsigned i=0;i<p.size();++i)p[i]=Byte((p[i]&14)|blue_[i]);break;
    }
    case Kind::blue_free:blue_.clear();break;
    case Kind::background_snap:background_=canvas_.drawing_page();break;
    case Kind::background_free:background_.clear();break;
    case Kind::background_rect: {
        auto& p=canvas_.drawing_page();if(background_.size()!=p.size())throw std::logic_error("Music background missing");
        for(int y=e.b;y<e.b+e.d;++y)for(int x=e.a;x<e.a+e.c;++x)if(x>=0 && x<640 && y>=0 && y<400)p[unsigned(y)*640+unsigned(x)]=background_[unsigned(y)*640+unsigned(x)];
        break;
    }
    case Kind::polygon: {
        if(e.a<3 || e.a>9 || e.data.size()!=unsigned(e.a+1)*4)throw std::invalid_argument("Music polygon event");
        std::vector<Point> p;for(unsigned i=0;i<e.data.size();i+=4)p.push_back({motion::wrap(e.data[i]|(unsigned(e.data[i+1])<<8)),motion::wrap(e.data[i+2]|(unsigned(e.data[i+3])<<8))});
        paint_polygon(canvas_.drawing_page(),p);break;
    }
    case Kind::access:canvas_.apply({K::access,e.a});break;
    case Kind::show:canvas_.apply({K::show,e.a});break;
    case Kind::clear:canvas_.drawing_page().assign(256000,0);break;
    case Kind::load: {cutscene::Event load(K::pi_load);load.name=std::string(e.data.begin(),e.data.end());std::transform(load.name.begin(),load.name.end(),load.name.begin(),[](unsigned char c){return char(c>='a' && c<='z' ? c-'a'+'A' : c);});canvas_.apply(load);break;}
    case Kind::palette:canvas_.apply({K::pi_palette});break;
    case Kind::picture:canvas_.apply({K::pi_put});break;
    case Kind::free:canvas_.apply({K::pi_free});break;
    case Kind::copy:canvas_.apply({K::copy_page,e.a});break;
    default:break; // State/timing and muted sound requests belong to Scene.
    }
}
Bytes Renderer::rgb(int tone) const {
    if(tone<0 || tone>100)throw std::invalid_argument("Music palette tone");
    const auto& page=canvas_.page(canvas_.shown_page());const auto& palette=canvas_.palette();Bytes result;result.reserve(page.size()*3);
    for(auto pixel:page)for(unsigned c=0;c<3;++c)result.push_back(Byte((palette[pixel*3+c]>>4)*unsigned(tone)/100*17));
    return result;
}
}

namespace th04::portable::op_music {
const std::array<std::string,24>& titles() {
    static const std::array<std::string,24> values{{
        "No.1   \214\266\221z\213\275  \201` Lotus Land Story",
        "No.2         Witching Dream       ",
        "No.3         Selene's light       ",
        "No.4  \221\225\217\374\220\355\201@\201` Decoration Battle",
        "No.5        Break the Sabbath     ",
        "No.6   \215g\213\277\213\310  \201` Scarlet Phoneme ",
        "No.7           Bad Apple!!        ",
        "No.8    \227\354\220\355\201@\201` Perdition crisis ",
        "No.9        \203A\203\212\203X\203}\203G\203X\203e\203\211      ",
        "No.10   \217\255\217\227\343Y\221z\213\310\201@\201` Capriccio  ",
        "No.11  \220\257\202\314\212\355\201@\201` Casket of Star  ",
        "No.12          Lotus Love         ",
        "No.13 \226\260\202\352\202\351\213\260\225| \201`Sleeping Terror",
        "No.14          Dream Land         ",
        "No.15   \227H\226\262\201@\201` Inanimate Dream  ",
        "No.16     \213\326\202\266\202\264\202\351\202\360\202\246\202\310\202\242\227V\213Y    ",
        "No.17 \203\201\203C\203h\214\266\221z\201@\201` Icemilk Magic",
        "No.18  \202\251\202\355\202\242\202\242\210\253\226\202\201@\201` Innocence ",
        "No.19             Days            ",
        "No.20           Peaceful          ",
        "No.21        Arcadian Dream       ",
        "No.22          \214\266\221z\202\314\217Z\220l         ",
        "                                  ",
        "            \201@\201@\202p\202\225\202\211\202\224          "
    }};return values;
}
const std::array<std::string,22>& songs() {
    static const std::array<std::string,22> values{{"op","st00","st10","st00b","st01","st01b","st02","st02b","st03","st03c","st03b","st04","st04b","st05","st05b","st06","st06b","st06c","end1","end2","staff","name"}};return values;
}
}

#include "point_numbers.hpp"
#include "main_state.hpp"
#include <fstream>
#include <iomanip>
#include <iostream>
#include <iterator>
#include <sstream>
#include <stdexcept>

namespace pn=th04::portable::pointnum;
using Bytes=std::vector<std::uint8_t>;
static void require(bool value,const char* message) {if(!value)throw std::runtime_error(message);}
static Bytes unhex(const std::string& text) {
    require(text.size()%2==0,"odd hex snapshot");Bytes result;
    for(unsigned i=0;i<text.size();i+=2) {
        const auto part=text.substr(i,2);std::size_t end=0;
        auto value=std::stoul(part,&end,16);require(end==2,"invalid hex snapshot");result.push_back(std::uint8_t(value));
    }
    return result;
}
static std::string hex(const Bytes& bytes) {
    std::ostringstream out;out<<std::hex<<std::setfill('0');
    for(auto value:bytes)out<<std::setw(2)<<unsigned(value);return out.str();
}
static unsigned word(const Bytes& bytes,unsigned at) {return bytes.at(at)|(unsigned(bytes.at(at+1))<<8);}
static void put(Bytes& bytes,unsigned value) {bytes.push_back(std::uint8_t(value));bytes.push_back(std::uint8_t(value>>8));}
static pn::Snapshot decode(const Bytes& data) {
    require(data.size()==7210,"complete portable snapshot");pn::Snapshot result;
    for(unsigned i=0;i<pn::count;++i) {
        unsigned at=i*16;auto& e=result.entities[i];e.flag=data[at];e.age=data[at+1];
        e.center={th04::portable::motion::wrap(word(data,at+2)),th04::portable::motion::wrap(word(data,at+4))};
        e.previous_y=th04::portable::motion::wrap(word(data,at+6));
        for(unsigned d=0;d<4;++d)e.decimal[d]=data[at+8+d];
        e.width=std::uint16_t(word(data,at+12));e.times_two=data[at+14];e.padding=data[at+15];
    }
    result.white_cursor=data[6400];result.yellow_cursor=data[6401];result.first_yellow=std::uint16_t(word(data,6402));
    for(unsigned i=0;i<401;++i)result.alive[i]=std::uint16_t(word(data,6404+i*2));
    // Last four bytes are untouched caller-owned sentinel state.
    return result;
}
static Bytes encode(const pn::Snapshot& state,const Bytes& input) {
    Bytes result;
    for(const auto& e:state.entities) {
        result.push_back(e.flag);result.push_back(e.age);put(result,unsigned(e.center.x));put(result,unsigned(e.center.y));
        put(result,unsigned(e.previous_y));for(auto digit:e.decimal)result.push_back(digit);
        put(result,e.width);result.push_back(e.times_two);result.push_back(e.padding);
    }
    result.push_back(state.white_cursor);result.push_back(state.yellow_cursor);put(result,state.first_yellow);
    for(auto pointer:state.alive)put(result,pointer);
    result.insert(result.end(),input.end()-4,input.end());return result;
}
static void contracts() {
    pn::System system;system.add({3072,1024},5120,true,true);
    require(system.draws().empty() && !system.snapshot().alive[0],"new popup must await update list");
    for(unsigned frame=0;frame<24;++frame)system.update();
    require(system.snapshot().entities[200].center.y==1024,"initial24 stationary ticks");
    system.update();require(system.snapshot().entities[200].center.y==1016,"delayed upward motion");
    system.prepare_render(true,399);
    require(system.draws().size()==7 && system.draws()[5].glyph==10 && system.draws()[6].glyph==11 &&
            system.draws()[0].color==11 && system.snapshot().entities[200].width==56,"yellow multiplier and width");
    for(unsigned frame=25;frame<37;++frame)system.update();
    require(system.snapshot().entities[200].flag==2 && !system.snapshot().alive[0],"age37 deferred release");
    system.update();require(!system.snapshot().entities[200].flag,"next tick frees removed popup");
    for(unsigned i=0;i<201;++i)system.add({int16_t(i),1024},1,false,false);
    require(system.snapshot().white_cursor==1 && system.snapshot().entities[0].center.x==200,"white ring overwrite");
    system.initialize();require(system.snapshot().entities[0].flag==1 && !system.snapshot().white_cursor,"init resets only cursors");
    // Real gameplay pickup goes through the event consumer and alive-list seam.
    namespace app=th04::portable::application;
    app::State application;application.start_normal(app::Playchar::reimu,app::ShotType::a);
    th04::portable::gameplay::State live(application,th04::portable::gameplay::Mode::actor_control);
    live.add_item({3072,5120},th04::portable::item::Type::bomb);live.update(0,false);
    require(live.point_numbers().snapshot().entities[0].flag==1 && live.point_numbers().draws().empty(),"actual pickup insertion seam");
    live.update(0,false);require(!live.point_numbers().draws().empty(),"actual next-tick popup render");
    for(unsigned i=0;i<72;++i)live.update(th04::portable::player::up,false);
    live.add_item(live.player().position().current,th04::portable::item::Type::point);
    live.update(0,false,true);
    const auto& yellow=live.point_numbers().snapshot().entities[200];
    require(yellow.flag==1 && yellow.times_two==1 && yellow.decimal[3]==5 &&
            live.item_events().events[0].collection.awarded_points==10240,"actual yellow/doubled pickup");
    live.update(0,false);require(live.point_numbers().draws()[0].color==11 &&
        live.point_numbers().draws().back().glyph==11,"actual yellow multiplier render");
    std::cout<<"pointnums=400_RING_LIFECYCLE multiplier=10_11 pickup=JOINED\n";
}
int main(int argc,char** argv) {
    try {
        if(argc==1) {contracts();return 0;}
        require(argc==3 || argc==5,"usage: --vectors FIXTURES [MAIN PIXELS]");
        require(std::string(argv[1])=="--vectors","point-number operation");
        std::ifstream input(argv[2]);require(bool(input),"point-number fixture input");
        std::unique_ptr<pn::Font> font;std::ofstream pixels;
        if(argc==5) {
            std::ifstream main(argv[3],std::ios::binary);require(bool(main),"MAIN font input");
            font=std::make_unique<pn::Font>(Bytes(std::istreambuf_iterator<char>(main),{}));
            pixels.open(argv[4],std::ios::binary);require(bool(pixels),"pixel output");
        }
        char operation;std::string snapshot;int x,y,points,yellow,times,scroll,line,seed;
        while(input>>operation>>snapshot>>x>>y>>points>>yellow>>times>>scroll>>line>>seed) {
            const auto data=unhex(snapshot);pn::System system(decode(data));
            if(operation=='I')system.initialize();
            else if(operation=='A')system.add({int16_t(x),int16_t(y)},std::uint16_t(points),yellow,times);
            else if(operation=='U')system.update();
            else if(operation=='R')system.prepare_render(scroll,std::uint16_t(line));
            else throw std::invalid_argument("unknown point-number vector");
            std::cout<<hex(encode(system.snapshot(),data))<<' '<<system.draws().size();
            for(const auto& draw:system.draws())std::cout<<' '<<draw.left<<' '<<draw.top<<' '<<draw.glyph<<' '<<unsigned(draw.color);
            std::cout<<'\n';
            if(font && operation=='R') {
                Bytes screen(640*400);for(unsigned i=0;i<screen.size();++i)screen[i]=std::uint8_t((i*73+seed)&15);
                for(const auto& draw:system.draws())pn::raster(*font,draw,[&](int px,int py,std::uint8_t color) {screen[unsigned(py)*640+unsigned(px)]=color;});
                pixels.write(reinterpret_cast<const char*>(screen.data()),std::streamsize(screen.size()));
            }
        }
        require(input.eof(),"truncated point-number fixture");return 0;
    } catch(const std::exception& error) {std::cerr<<error.what()<<'\n';return 1;}
}

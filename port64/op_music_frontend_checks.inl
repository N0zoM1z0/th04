// Actual options/menu -> Music Room twice -> retained OP -> ordinary MAIN.
// The source archive and physical score file are inputs; no actor control is used.
void run_op_music_checks(const PiImage& background,const CdgSheet& numerals,
    const CdgSheet& labels,const CdgSheet& cursors,const PiImage& selection_background,
    const CdgSheet& portraits,const MainAssets& assets,const std::string& destination) {
    namespace fs=std::filesystem;const fs::path directory(destination),inputs(assets.save_directory);
    require_view(!fs::exists(directory) && assets.muted,"Music Room checks need fresh muted outputs");fs::create_directories(directory);
    const auto read=[](const fs::path& path) {std::ifstream f(path,std::ios::binary);require_view(bool(f),"Music input missing");return Bytes(std::istreambuf_iterator<char>(f),{});};
    const auto hex=[](std::ostream& out,const auto& bytes) {
        const char* digits="0123456789abcdef";if(bytes.empty())out<<'-';
        for(auto v:bytes)out<<digits[unsigned(v)>>4]<<digits[unsigned(v)&15];
    };
    const auto state_bytes=[](const op_music::State& state) {
        Bytes b;for(const auto& p:state.polygons)for(int v:{int(p.center.x),int(p.center.y),int(p.velocity.x),int(p.velocity.y)}) {b.push_back(std::uint8_t(v));b.push_back(std::uint8_t(unsigned(v)>>8));}
        for(const auto& p:state.polygons)b.push_back(p.angle);
        for(const auto& p:state.polygons)b.push_back(p.angle_speed);
        return b;
    };
    std::ifstream cases(inputs/"cases.txt");require_view(bool(cases),"Music Room index missing");std::string name;unsigned rank,count=0;
    while(cases>>name>>rank) {
        require_view(rank<4 && name.find('/')==std::string::npos && name.find("..") ==std::string::npos,"Music case name/rank");
        const auto location=directory/name;fs::create_directories(location/"save");auto input=assets;input.save_directory=(location/"save").string();
        fs::copy_file(inputs/"scores.SCR",location/"save"/"GENSOU.SCR");
        FrontEnd scene(background,numerals,labels,cursors,selection_background,portraits,&input);scene.enable_registration();
        while(scene.menu_state().selection()!=unsigned(menu::MainChoice::options))scene.input(menu::Input::down);
        scene.input(menu::Input::confirm);while(scene.menu_state().options().rank!=rank)scene.input(menu::Input::right);scene.input(menu::Input::cancel);
        const auto generation=scene.generation(),resident=scene.resident().random_seed_source;
        for(unsigned visit=0;visit<2;++visit) {
            const auto visit_dir=location/("visit"+std::to_string(visit));fs::create_directories(visit_dir);
            while(scene.menu_state().selection()!=unsigned(menu::MainChoice::music_room))scene.input(menu::Input::down);
            const auto initial=scene.music_state();const auto seed=scene.process_random_state();const auto keys=read(inputs/(name+".keys"));require_view(!(keys.size()%2),"Music keys shape");
            std::ofstream fixture(visit_dir/"caller.txt",std::ios::binary);
            fixture<<initial.initialized<<' '<<+initial.playing<<' '<<seed<<' ';hex(fixture,state_bytes(initial));fixture<<' ';hex(fixture,assets.music.comments);fixture<<' ';hex(fixture,keys);fixture<<'\n';fixture.close();
            std::ofstream trace(visit_dir/"events.txt",std::ios::binary);
            scene.set_music_observer([&](const op_music::Event& e){trace<<op_music::kind_name(e.kind)<<' '<<e.tick<<' '<<e.a<<' '<<e.b<<' '<<e.c<<' '<<e.d<<' ';hex(trace,e.data);trace<<'\n';});
            scene.input(menu::Input::confirm);require_view(scene.music_scene() && scene.animated(),"Music scene did not open");
            require_view(visit || scene.music_draws()==96,"Music first frame RNG");
            unsigned ticks=0;
            while(scene.music_scene() && ticks<200) {
                ++ticks;const unsigned at=ticks*2;const auto key=std::uint16_t(at+1<keys.size() ? keys[at]|(unsigned(keys[at+1])<<8) : 0);
                const std::uint16_t held=std::uint16_t((key&15)|(key&0x20)|((key&0x1000) ? 0x2000 : 0)|((key&0x2000) ? 0x1000 : 0));
                scene.advance(held,false,true);require_view(scene.generation()==generation && scene.program()==application::Program::op,"Music replaced its OP");
                if(scene.music_scene()) {
                    require_view(scene.resident().random_seed_source==resident+visit,"Music advanced resident seed during child");
                    const auto pixels=scene.frame().pixels;const auto rng=scene.process_random_state();const auto polygons=state_bytes(scene.music_state());
                    scene.repaint();scene.repaint();require_view(scene.frame().pixels==pixels && scene.process_random_state()==rng && state_bytes(scene.music_state())==polygons,"Music repaint advanced simulation");
                    if(ticks<=14 || ticks%20==0)write_bmp((visit_dir/("tick"+std::to_string(ticks)+".bmp")).string(),scene.frame());
                }
            }
            require_view(!scene.music_scene() && ticks<200 && scene.resident().random_seed_source==resident+visit+1 &&
                scene.menu_state().selection()==0 && scene.menu_state().options().rank==rank && scene.resident().config.rank==rank,"Music return/order/config");
            const auto& s=scene.music_state();trace<<"END "<<ticks<<" 0 "<<scene.process_random_state()<<' '<<scene.music_draws()<<' '<<s.initialized<<' '<<+s.playing<<' '<<+s.selected<<' '<<+s.page<<' '<<+s.comment_shown<<' '<<s.text_effect<<' ';
            hex(trace,state_bytes(s));trace<<' ';hex(trace,s.comment);trace<<'\n';trace.close();scene.set_music_observer({});
            std::ofstream parent(visit_dir/"parent.txt",std::ios::binary);for(const auto& request:scene.music_return_requests())parent<<request<<'\n';parent.close();
            write_bmp((visit_dir/"returned.bmp").string(),scene.frame());
            require_view(scene.frame().pixels==render_menu(background,numerals,labels,cursors,scene.menu_state()).pixels,"Music active menu assets differ after reload");
        }
        require_view(read(location/"save"/"GENSOU.SCR")==read(inputs/"scores.SCR"),"Music changed score file");
        scene.input(menu::Input::confirm);scene.input(menu::Input::confirm);scene.input(menu::Input::confirm);
        require_view(scene.live_main() && scene.main_resources_alive() && scene.resident().config.rank==rank,"Music return failed ordinary MAIN");
        std::cout<<"OP_MUSIC "<<name<<" visits=2 retained_op=1 main_rank="<<rank<<" muted=1\n";++count;
    }
    require_view(cases.eof() && count>0,"Music index malformed");
}

// Real menu/options -> ranking blocking caller -> retained OP/menu -> MAIN.
// Input score files and tick masks are supplied by the original OP verifier.
void run_op_ranking_checks(const PiImage& background,const CdgSheet& numerals,
    const CdgSheet& labels,const CdgSheet& cursors,const PiImage& selection_background,
    const CdgSheet& portraits,const MainAssets& assets,const std::string& destination) {
    namespace fs=std::filesystem;
    const fs::path directory(destination),inputs(assets.save_directory);
    const auto read=[](const fs::path& path) {
        std::ifstream f(path,std::ios::binary);require_view(bool(f),"ranking file missing");
        return Bytes(std::istreambuf_iterator<char>(f),{});
    };
    require_view(!fs::exists(directory) && assets.muted,"ranking checks require fresh muted outputs");fs::create_directories(directory);
    const auto hex=[](std::ostream& out,const auto& bytes) {
        const char* digits="0123456789abcdef";
        if(bytes.empty())out<<'-';
        for(auto value:bytes)out<<digits[unsigned(value)>>4]<<digits[unsigned(value)&15];
    };
    std::ifstream cases(inputs/"cases.txt");require_view(bool(cases),"ranking input index missing");
    std::string name;unsigned rank,count=0;
    while(cases>>name>>rank) {
        require_view(rank<4 && name.find('/')==std::string::npos && name.find("..") ==std::string::npos,"ranking fixture name/rank");
        const auto location=directory/name;fs::create_directories(location/"save");auto input=assets;input.save_directory=(location/"save").string();
        fs::copy_file(inputs/"scores.SCR",location/"save"/"GENSOU.SCR");
        FrontEnd scene(background,numerals,labels,cursors,selection_background,portraits,&input);scene.enable_registration();
        while(scene.menu_state().selection()!=unsigned(menu::MainChoice::options))scene.input(menu::Input::down);
        scene.input(menu::Input::confirm);
        while(scene.menu_state().options().rank!=rank)scene.input(menu::Input::right);
        scene.input(menu::Input::cancel);scene.input(menu::Input::up);scene.input(menu::Input::up);
        require_view(scene.menu_state().selection()==unsigned(menu::MainChoice::scores),"ranking selected wrong menu entry");
        const auto initial=scene.op_scores().snapshot();const auto generation=scene.generation(),seed=scene.process_random_state();const auto resident=scene.resident().random_seed_source;
        std::ofstream fixture(location/"caller.txt",std::ios::binary);
        fixture<<rank<<' '<<+initial.rank<<' '<<+initial.extra_unlocked<<" 1 "<<seed<<' ';hex(fixture,initial.first);fixture<<' ';hex(fixture,initial.second);fixture<<' ';
        for(const auto& col:initial.cleared)hex(fixture,col);fixture<<' ';hex(fixture,read(location/"save"/"GENSOU.SCR"));fixture<<' ';
        const auto raw=read(inputs/(name+".keys"));require_view(!(raw.size()%2),"ranking input shape");hex(fixture,raw);fixture<<'\n';fixture.close();
        std::ofstream trace(location/"events.txt",std::ios::binary);
        scene.set_ranking_observer([&](const op_ranking::Event& e) {
            trace<<op_ranking::kind_name(e.kind)<<' '<<e.tick<<' '<<e.a<<' '<<e.b<<' '<<e.c<<' '<<e.d<<' ';hex(trace,e.data);trace<<'\n';
        });
        const auto before=scene.frame();write_bmp((location/"before.bmp").string(),before);
        {std::ofstream indices(location/"before.idx",std::ios::binary);indices.write(reinterpret_cast<const char*>(before.indices.data()),std::streamsize(before.indices.size()));require_view(bool(indices),"ranking initial indexed capture failed");}
        scene.input(menu::Input::confirm);
        require_view(scene.ranking_scene() && scene.animated() && scene.program()==application::Program::op,"ranking caller failed to open");
        unsigned ticks=0,captures=0;
        while(scene.ranking_scene() && ticks<500) {
            ++ticks;const unsigned at=ticks*2;const auto key=std::uint16_t(at+1<raw.size() ? unsigned(raw[at])|(unsigned(raw[at+1])<<8) : 0);
            // Original key_det -> MAIN host masks. Single mappings preserve
            // physical Enter/Esc distinctions before the frontend bridge.
            const std::uint16_t held=std::uint16_t((key&15)|((key&0x20) ? 0x20 : 0)|((key&0x1000) ? 0x2000 : 0)|((key&0x2000) ? 0x1000 : 0)|((key&0x10) ? 0x800 : 0));
            scene.advance(held,false,true);
            require_view(scene.generation()==generation && scene.program()==application::Program::op,"ranking replaced its OP process");
            if(scene.ranking_scene()) {
                require_view(scene.resident().random_seed_source==resident,"ranking advanced parent resident RNG during child");
                const auto pixels=scene.frame().pixels;const auto random=scene.process_random_state();scene.repaint();scene.repaint();
                require_view(scene.frame().pixels==pixels && scene.process_random_state()==random,"ranking repaint changed state");
                if(ticks%18==0 || ticks==37) {write_bmp((location/("tick"+std::to_string(ticks)+".bmp")).string(),scene.frame());++captures;}
            }
        }
        require_view(!scene.ranking_scene() && ticks<500 && scene.resident().random_seed_source==resident+1 &&
            scene.resident().config.rank==rank && scene.menu_state().selection()==unsigned(menu::MainChoice::scores),"ranking failed retained OP return");
        write_bmp((location/"returned.bmp").string(),scene.frame());
        require_view(scene.frame().pixels==before.pixels,"ranking did not restore title selection");
        const auto& result=scene.op_scores().snapshot();trace<<"END "<<ticks<<" 100 "<<scene.process_random_state()<<" 0 1 "<<+result.rank<<' '<<+result.extra_unlocked<<' ';
        hex(trace,result.first);trace<<' ';hex(trace,result.second);trace<<' ';for(const auto& col:result.cleared)hex(trace,col);trace<<' ';hex(trace,read(location/"save"/"GENSOU.SCR"));trace<<'\n';trace.close();
        require_view(result.cleared==initial.cleared && result.extra_unlocked==initial.extra_unlocked,"ranking changed unlock scan");
        scene.input(menu::Input::up);scene.input(menu::Input::up);
        while(scene.menu_state().selection()!=unsigned(menu::MainChoice::game))scene.input(menu::Input::up);
        scene.input(menu::Input::confirm);scene.input(menu::Input::confirm);scene.input(menu::Input::confirm);
        require_view(scene.live_main() && scene.resident().config.rank==rank && scene.main_resources_alive(),"MAIN did not use configured rank after ranking browse");
        std::cout<<"OP_RANKING "<<name<<" ticks="<<ticks<<" captures="<<captures<<" same_op=1 main_rank="<<rank<<" muted=1\n";++count;
    }
    require_view(cases.eof() && count>0,"ranking input index malformed");
}

void finish_setup_for_check(FrontEnd&,unsigned,unsigned);
// Configuration-enabled real menus; older seeded component scenes do not
// enable this owner and retain their independent historical fixture scope.
void run_configuration_checks(const PiImage& background,const CdgSheet& numerals,
    const CdgSheet& labels,const CdgSheet& cursors,const PiImage& selection_background,
    const CdgSheet& portraits,const MainAssets& assets,const std::string& destination) {
    namespace fs=std::filesystem;namespace cfg=th04::portable::configuration;
    const fs::path out(destination),inputs(assets.save_directory);
    require_view(assets.muted && !fs::exists(out),"configuration controls need fresh muted outputs");fs::create_directories(out);
    unsigned phase=99;std::ifstream(inputs/"phase.txt")>>phase;require_view(phase<2,"configuration check phase");
    const auto read=[](const fs::path& p) {std::ifstream f(p,std::ios::binary);require_view(bool(f),"configuration capture read");return Bytes(std::istreambuf_iterator<char>(f),{});};
    const auto write=[](const fs::path& p,const Bytes& b) {std::ofstream f(p,std::ios::binary);f.write(reinterpret_cast<const char*>(b.data()),b.size());require_view(bool(f),"configuration capture write");};
    for(unsigned rank=0;rank<4;++rank)for(unsigned kind=0;kind<2;++kind) {
        const auto name="r"+std::to_string(rank)+"-k"+std::to_string(kind);const auto dir=out/name,save=inputs/name;
        fs::create_directories(dir);fs::create_directories(save);
        if(!phase) {
            fs::copy_file(inputs/"scores.SCR",save/"GENSOU.SCR");
            const auto seed=inputs/(name+".cfg");if(fs::exists(seed))fs::copy_file(seed,save/"MIKO.CFG");
        }
        auto input=assets;input.save_directory=save.string();
        FrontEnd scene(background,numerals,labels,cursors,selection_background,portraits,&input);
        scene.enable_configuration();scene.enable_registration();
        if(scene.setup_scene())finish_setup_for_check(scene,2,1);
        const menu::Options wanted{std::uint8_t(rank),std::uint8_t(6-rank),std::uint8_t(rank%3),
            std::uint8_t((rank+unsigned(phase && kind))%3),std::uint8_t((3-rank)%3),rank%2==0};
        if(phase) {
            require_view(scene.menu_state().options()==wanted,"separate-process configuration reload");
        } else {
            const auto before=read(save/"MIKO.CFG");write(dir/"before.cfg",before);
            while(scene.menu_state().selection()!=unsigned(menu::MainChoice::options))scene.input(menu::Input::down);
            scene.input(menu::Input::confirm);
            const auto desired=cfg::encode(wanted);
            for(unsigned field=0;field<6;++field) {
                unsigned attempts=0;
                while(cfg::encode(scene.menu_state().options())[field]!=desired[field]) {
                    scene.input(menu::Input::right);require_view(++attempts<8,"configuration menu control wrap");
                }
                scene.input(menu::Input::down);
            }
            scene.input(menu::Input::cancel);
            while(scene.menu_state().selection()!=0)scene.input(menu::Input::up);
            require_view(read(save/"MIKO.CFG")==before,"configuration saved before real boundary");
            if(kind) {
                scene.advance(0x2000,false,false);
                for(unsigned i=0;i<640;++i)scene.advance(0,false,false);
                scene.advance(0,false,false);for(unsigned i=0;i<18;++i)scene.advance(0,false,false);
            } else {
                scene.input(menu::Input::confirm);scene.input(menu::Input::confirm);scene.input(menu::Input::confirm);
            }
            require_view(scene.live_main(),"configuration MAIN entry");write(dir/"live.cfg",read(save/"MIKO.CFG"));
            if(kind) {
                require_view(scene.main_state().rank()==2 && scene.main_state().turbo(),"demo config local override");
                scene.advance(0x2000,false,false);
                // A different closed physical config must be read by fresh OP.
                auto changed=read(save/"MIKO.CFG");changed[3]=std::uint8_t((rank+1)%3);
                unsigned sum=0;for(unsigned i=0;i<6;++i)sum+=changed[i];changed[9]=std::uint8_t(sum);write(save/"MIKO.CFG",changed);
                for(unsigned i=0;i<171;++i)scene.advance(0,false,false);
                auto returned=wanted;returned.bgm_mode=std::uint8_t((rank+1)%3);
                require_view(scene.program()==application::Program::op && scene.menu_state().options()==returned,"fresh OP did not reload closed configuration");
                scene.input(menu::Input::cancel);
            } else {
                require_view(scene.main_state().rank()==rank && scene.main_state().turbo()==wanted.turbo &&
                    scene.resident().credit_lives==wanted.lives && scene.resident().credit_bombs==wanted.bombs,"ordinary MAIN configuration");
                scene.advance(0,false,false);
                FrontEnd reopen(background,numerals,labels,cursors,selection_background,portraits,&input);
                reopen.enable_configuration();reopen.enable_registration();
                require_view(reopen.menu_state().options()==wanted,"configuration object restart");reopen.close_window();
            }
            write(dir/"exit.cfg",read(save/"MIKO.CFG"));
        }
        if(phase) {
            scene.input(menu::Input::confirm);scene.input(menu::Input::confirm);scene.input(menu::Input::confirm);
            require_view(scene.live_main() && scene.resident().config==wanted,"restarted MAIN options");
            write(dir/"restarted.cfg",read(save/"MIKO.CFG"));
        }
        scene.repaint();write_bmp((dir/"view.bmp").string(),scene.frame());
        std::cout<<"CONFIG rank="<<rank<<" route="<<kind<<" phase="<<phase<<" muted=1\n";
    }
    if(!phase) {
        const auto dir=out/"extra";fs::create_directories(dir/"save");
        fs::copy_file(inputs/"scores.SCR",dir/"save"/"GENSOU.SCR");
        fs::copy_file(inputs/"r0-k0.cfg",dir/"save"/"MIKO.CFG");
        auto input=assets;input.save_directory=(dir/"save").string();
        FrontEnd scene(background,numerals,labels,cursors,selection_background,portraits,&input);
        scene.enable_configuration();scene.enable_registration();
        require_view(scene.op_scores().extra_unlocked(),"physical score fixture must unlock Extra");
        const menu::Options wanted{3,6,0,0,2,false};const auto desired=cfg::encode(wanted);
        while(scene.menu_state().selection()!=unsigned(menu::MainChoice::options))scene.input(menu::Input::down);
        scene.input(menu::Input::confirm);
        for(unsigned field=0;field<6;++field) {
            unsigned attempts=0;while(cfg::encode(scene.menu_state().options())[field]!=desired[field]) {
                scene.input(menu::Input::right);require_view(++attempts<8,"Extra configuration wrap");
            }
            scene.input(menu::Input::down);
        }
        scene.input(menu::Input::cancel);
        while(scene.menu_state().selection()!=unsigned(menu::MainChoice::extra))scene.input(menu::Input::up);
        scene.input(menu::Input::confirm);scene.input(menu::Input::confirm);scene.input(menu::Input::confirm);
        require_view(scene.live_main() && scene.resident().stage==6 && scene.resident().config==wanted &&
            scene.resident().credit_lives==3 && scene.resident().credit_bombs==2,"Extra altered saved configurable resources");
        write(dir/"live.cfg",read(dir/"save"/"MIKO.CFG"));scene.repaint();write_bmp((dir/"view.bmp").string(),scene.frame());
        std::cout<<"CONFIG_EXTRA physical_unlock=1 saved_lives=6 saved_bombs=0 credit_lives=3 credit_bombs=2 muted=1\n";
    }
    if(!phase)for(unsigned boundary=0;boundary<4;++boundary) {
        const auto dir=out/("failed"+std::to_string(boundary));fs::create_directories(dir);
        auto input=assets;input.save_directory=(dir/"save").string();
        FrontEnd scene(background,numerals,labels,cursors,selection_background,portraits,&input);
        scene.enable_configuration();scene.enable_registration();
        const fs::path path=fs::path(input.save_directory)/"MIKO.CFG";
        if(scene.setup_scene())finish_setup_for_check(scene,2,1);
        fs::rename(path,dir/"previous.cfg");fs::create_directory(path);bool rejected=false;
        try {
            if(boundary==0) {scene.input(menu::Input::confirm);scene.input(menu::Input::confirm);scene.input(menu::Input::confirm);}
            else if(boundary==1) {for(unsigned i=0;i<641+18;++i)scene.advance(0,false,false);}
            else if(boundary==2)scene.input(menu::Input::cancel);
            else scene.close_window();
        } catch(const std::exception&) {rejected=true;}
        require_view(rejected && scene.program()==application::Program::op && !scene.live_main() && fs::is_directory(path),"failed configuration write advanced process");
        for(const auto& p:fs::directory_iterator(path.parent_path()))require_view(p.path().filename().string().find(".config-pending-")!=0,"configuration failure leaked temp");
        std::ofstream(dir/"rejected.txt",std::ios::binary)<<"failed="<<boundary<<" program=op main=0 muted=1\n";
        std::cout<<"CONFIG_FAILED boundary="<<boundary<<" muted=1\n";
    }
}

// Deliberate released/pressed actions, through the same owner as both GUIs.
void finish_setup_for_check(FrontEnd& scene,unsigned bgm=2,unsigned se=1) {
    for(unsigned menu=0;menu<2;++menu) {
        unsigned ticks=0;
        while(scene.setup_scene() && (scene.setup_scene()->submenu()!=menu || !scene.setup_scene()->awaiting_input())) {
            scene.advance(0,false,false);require_view(++ticks<500,"setup menu did not reach input");
        }
        require_view(scene.setup_scene(),"setup ended before both selections");
        for(unsigned i=0;i<4;++i)scene.advance(0,false,false);
        const auto wanted=menu ? se : bgm;
        for(unsigned guard=0;scene.setup_scene()->selected()!=wanted;++guard) {
            require_view(guard<3,"setup option cycling");scene.advance(menu ? 2 : 1,false,false);
            for(unsigned i=0;i<5;++i)scene.advance(0,false,false);
        }
        // Both arrows in this sample must lose to Enter.
        scene.advance(0x1003,false,false);scene.advance(0,false,false);
    }
    unsigned ticks=0;while(scene.setup_scene()) {scene.advance(0,false,false);require_view(++ticks<500,"setup fade did not return");}
}
void run_setup_checks(const PiImage& background,const CdgSheet& numerals,const CdgSheet& labels,
    const CdgSheet& cursors,const PiImage& selection_background,const CdgSheet& portraits,
    const MainAssets& assets,const std::string& destination) {
    namespace fs=std::filesystem;namespace cfg=th04::portable::configuration;
    const fs::path out(destination),inputs(assets.save_directory);require_view(assets.muted && !fs::exists(out),"setup checks require fresh muted outputs");fs::create_directories(out);
    unsigned phase=99;std::ifstream(inputs/"phase.txt")>>phase;require_view(phase<2,"setup check phase");
    const auto read=[](const fs::path& p) {std::ifstream f(p,std::ios::binary);require_view(bool(f),"setup read");return Bytes(std::istreambuf_iterator<char>(f),{});};
    const auto write=[](const fs::path& p,const Bytes& b) {std::ofstream f(p,std::ios::binary);f.write(reinterpret_cast<const char*>(b.data()),b.size());require_view(bool(f),"setup write");};
    for(unsigned bgm=0;bgm<3;++bgm)for(unsigned se=0;se<3;++se) {
        const auto name="b"+std::to_string(bgm)+"-s"+std::to_string(se);const auto dir=out/name,save=inputs/name;
        fs::create_directories(dir);fs::create_directories(save);
        if(!phase) {
            fs::copy_file(inputs/"scores.SCR",save/"GENSOU.SCR");
            const auto seed=inputs/(name+".cfg");if(fs::exists(seed))fs::copy_file(seed,save/"MIKO.CFG");
        }
        auto input=assets;input.save_directory=save.string();
        FrontEnd scene(background,numerals,labels,cursors,selection_background,portraits,&input);
        std::ofstream trace(dir/"events.txt",std::ios::binary);
        scene.set_setup_observer([&](const th04::portable::op_setup::Event& e) {
            trace<<th04::portable::op_setup::kind_name(e.kind)<<' '<<e.tick<<' '<<e.a<<' '<<e.b<<' '<<e.c<<' '<<e.d<<' ';
            if(e.data.empty())trace<<'-';else {const char* h="0123456789abcdef";for(auto v:e.data)trace<<h[v>>4]<<h[v&15];}trace<<'\n';
        });
        scene.enable_configuration();scene.enable_registration();
        if(!phase) {
            require_view(scene.setup_scene() && !scene.live_main() && scene.program()==application::Program::op,"first setup startup owner missing");
            const auto before=read(save/"MIKO.CFG"),score=read(save/"GENSOU.SCR");write(dir/"before.cfg",before);
            require_view(before[0]==255 && scene.resident().random_seed_source==0 && scene.process_random_state()==1,"setup sentinel/RNG isolation");
            scene.input(menu::Input::confirm);scene.input(menu::Input::cancel);
            require_view(scene.setup_scene() && !scene.live_main(),"menu actions bypassed setup");
            scene.repaint();write_bmp((dir/"black.bmp").string(),scene.frame());
            for(unsigned i=0;i<38;++i)scene.advance(0,false,false);
            require_view(scene.setup_scene()->awaiting_input(),"setup window did not open in original38refreshes");
            scene.repaint();write_bmp((dir/"bgm.bmp").string(),scene.frame());
            finish_setup_for_check(scene,bgm,se);scene.repaint();write_bmp((dir/"menu.bmp").string(),scene.frame());
            require_view(scene.resident().config.rank==1 && scene.resident().config.bgm_mode==bgm && scene.resident().config.se_mode==se && scene.resident().random_seed_source==0,"setup selected options/resident seed");
            require_view(read(save/"MIKO.CFG")==before,"setup saved before OP exit/entry");
            require_view(read(save/"GENSOU.SCR")==score && scene.op_scores().extra_unlocked(),"setup lost physical score/unlock");
            scene.close_window();write(dir/"exit.cfg",read(save/"MIKO.CFG"));
        } else {
            require_view(!scene.setup_scene() && scene.menu_state().options().bgm_mode==bgm && scene.menu_state().options().se_mode==se,"setup repeats after committed restart");
            scene.input(menu::Input::confirm);scene.input(menu::Input::confirm);scene.input(menu::Input::confirm);
            require_view(scene.live_main() && scene.main_state().rank()==1 && scene.resident().config.bgm_mode==bgm && scene.resident().config.se_mode==se,"restart MAIN setup options");
            write(dir/"restarted.cfg",read(save/"MIKO.CFG"));scene.repaint();write_bmp((dir/"main.bmp").string(),scene.frame());
        }
        std::cout<<"SETUP bgm="<<bgm<<" se="<<se<<" phase="<<phase<<" muted=1\n";
    }
    if(!phase) {
        const auto dir=out/"interrupted";fs::create_directories(dir/"save");
        auto input=assets;input.save_directory=(dir/"save").string();
        FrontEnd first(background,numerals,labels,cursors,selection_background,portraits,&input);first.enable_configuration();first.enable_registration();
        for(unsigned i=0;i<42;++i)first.advance(0,false,false);
        first.advance(0x1000,false,false);for(unsigned i=0;i<45;++i)first.advance(0,false,false);
        require_view(first.setup_scene() && first.setup_scene()->submenu()==1,"interrupted setup did not reach SE");
        first.close_window();require_view(read(dir/"save/MIKO.CFG")[0]==255,"unfinished setup published normal rank");
        FrontEnd reopen(background,numerals,labels,cursors,selection_background,portraits,&input);reopen.enable_configuration();reopen.enable_registration();
        require_view(reopen.setup_scene() && reopen.setup_scene()->submenu()==0,"unfinished setup restart skipped BGM");
        finish_setup_for_check(reopen);reopen.close_window();write(dir/"exit.cfg",read(dir/"save/MIKO.CFG"));
        const auto blocked=out/"failed";fs::create_directories(blocked/"save");input.save_directory=(blocked/"save").string();
        FrontEnd failed(background,numerals,labels,cursors,selection_background,portraits,&input);failed.enable_configuration();failed.enable_registration();
        fs::remove(blocked/"save/MIKO.CFG");fs::create_directory(blocked/"save/MIKO.CFG");bool rejected=false;
        try {failed.close_window();}catch(const std::exception&) {rejected=true;}
        require_view(rejected && failed.program()==application::Program::op && failed.setup_scene() && !failed.live_main(),"failed pending config save crossed OP boundary");
        for(const auto& p:fs::directory_iterator(blocked/"save"))require_view(p.path().filename().string().find(".config-pending-")!=0,"setup failed-save temporary survived");
        std::ofstream(blocked/"rejected.txt",std::ios::binary)<<"program=op setup=1 main=0 muted=1\n";
        const auto fresh=out/"fresh-op";fs::create_directories(fresh/"save");input.save_directory=(fresh/"save").string();
        fs::copy_file(inputs/"scores.SCR",fresh/"save/GENSOU.SCR");
        write(fresh/"save/MIKO.CFG",Bytes{1,3,2,2,1,1,0,0,0,10});
        FrontEnd returned(background,numerals,labels,cursors,selection_background,portraits,&input);returned.enable_configuration();returned.enable_registration();
        for(unsigned i=0;i<659;++i)returned.advance(0,false,false);
        require_view(returned.live_main(),"setup fresh-OP control did not enter idle demo");
        write(fresh/"save/MIKO.CFG",Bytes{255,3,2,1,1,1,0,0,0,7});
        returned.advance(0x2000,false,false);for(unsigned i=0;i<171;++i)returned.advance(0,false,false);
        require_view(returned.program()==application::Program::op && returned.setup_scene(),"fresh OP ignored physical rankFF");
        finish_setup_for_check(returned,1,2);returned.close_window();write(fresh/"exit.cfg",read(fresh/"save/MIKO.CFG"));
        std::cout<<"SETUP_INTERRUPTED restart=1 failed_writer=1 fresh_op=1 muted=1\n";
    }
}

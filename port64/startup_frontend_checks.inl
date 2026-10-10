// Real frontend startup/configuration, ordinary MAIN contact/Quit and fresh OP.
// The finite STD below is an authored legal input fixture, not a full route.
// A second host invocation reopens the same files with a new resident owner.
void run_startup_checks(const PiImage& background,const CdgSheet& numerals,
    const CdgSheet& labels,const CdgSheet& cursors,const PiImage& selection_background,
    const CdgSheet& portraits,const MainAssets& assets,const std::string& destination) {
    namespace fs=std::filesystem;namespace startup=th04::portable::op_startup;
    namespace cfg=th04::portable::configuration;
    const fs::path out(destination),inputs(assets.save_directory);
    require_view(assets.muted && assets.full_startup && assets.pmd_profile && !fs::exists(out),
        "startup checks require fresh muted outputs and a resident profile");
    unsigned phase=99;std::ifstream(inputs/"phase.txt")>>phase;
    require_view(phase<2,"startup restart phase missing");fs::create_directories(out);
    const auto read=[](const fs::path& p) {
        std::ifstream f(p,std::ios::binary);require_view(bool(f),"startup read failed");
        return Bytes(std::istreambuf_iterator<char>(f),{});
    };
    for(unsigned index=0;index<11;++index) {
        const unsigned bgm=index<9 ? index/3 : index==9 ? 2 : 0;
        const unsigned se=index<9 ? index%3 : index==9 ? 1 : 2;
        const auto name=std::to_string(index);const auto folder=out/name,save=inputs/name;
        fs::create_directories(folder);fs::create_directories(save);
        if(!phase) {
            if(index<9) {
                cfg::HostStore store(save);store.complete_setup(std::uint8_t(bgm),std::uint8_t(se));
                auto options=store.options();options.lives=1;store.save(options,false);
            } else if(index==10)std::ofstream(save/"MIKO.CFG",std::ios::binary)<<"bad";
        }
        const auto score_path=save/"GENSOU.SCR";
        const auto old_score=phase ? read(score_path) : Bytes{};
        auto input=assets;input.save_directory=save.string();
        // One zero-score enemy crosses the unchanged player's position.
        Bytes standard{0,0,8};standard.insert(standard.end(),8,0);standard.push_back(9);
        standard.insert(standard.end(),8,16);standard.push_back(0);standard.push_back(1);
        for(unsigned v:{9u,0x10u,128u,1u,0u,0u,0u,6u,100u,0u})standard.push_back(std::uint8_t(v));
        standard.push_back(0);
        for(unsigned v:{64u,0u,1u,0u,0u,12u,0u,20u,255u,0u,0u})standard.push_back(std::uint8_t(v));
        for(unsigned v:{208u,7u,1u,0u,0u,12u,0u,19u,255u,0u,0u})standard.push_back(std::uint8_t(v));
        standard.insert(standard.end(),2,0);const auto extent=standard.size()-2;
        standard[0]=std::uint8_t(extent);standard[1]=std::uint8_t(extent>>8);input.standard=standard;
        FrontEnd scene(background,numerals,labels,cursors,selection_background,portraits,&input);
        std::ofstream events(folder/"events.txt",std::ios::binary),state(folder/"state.txt",std::ios::binary);
        std::ofstream pcm(folder/"mixed.pcm",std::ios::binary);
        unsigned logos=0,completions=0,title_loads=0;std::uint32_t startup_random=0;
        scene.set_stereo_observer([&](auto program,auto generation,const auto& samples) {
            state<<"PCM "<<unsigned(program)<<' '<<generation<<' '<<samples.size()<<'\n';
            for(auto sample:samples)for(auto word:{sample.left,sample.right}) {
                pcm.put(char(std::uint16_t(word)&255));pcm.put(char(std::uint16_t(word)>>8));
            }
        });
        scene.set_startup_observer([&](const startup::Event& e) {
            events<<scene.generation()<<' '<<startup::kind_name(e.kind)<<' '<<e.tick<<' '<<e.a<<' '<<e.b<<' '<<e.c<<' ';
            const char* hex="0123456789abcdef";if(e.data.empty())events<<'-';
            else {for(auto v:e.data)events<<hex[v>>4]<<hex[v&15];}
            events<<'\n';
            if(e.kind==startup::Kind::logo_complete) {
                ++logos;require_view(scene.resident().zunsoft_shown,"logo resident flag published after title");
            }
            if(e.kind==startup::Kind::load && e.data==Bytes{'o','p','5','b','.','p','i'})++title_loads;
            if(e.kind==startup::Kind::super_load && bgm) {
                const auto measure=scene.resident_sound()->command(0x500);
                require_view(measure>=2,"logo bypassed the actual PMD measure wait");
            }
            if(e.kind==startup::Kind::complete) {
                ++completions;startup_random=scene.startup_scene()->random_state();
                if(!phase && completions==1)require_view(!fs::exists(score_path),"score published before startup returned");
            }
        });
        scene.enable_configuration();scene.enable_registration();
        require_view(!scene.resident().zunsoft_shown,"new application inherited logo flag");
        if(!phase && index>=9) {
            require_view(scene.setup_scene() && !scene.startup_scene(),"missing/bad configuration skipped first setup");
            finish_setup_for_check(scene,bgm,se);
        }
        require_view(!scene.setup_scene() && scene.startup_scene() && !scene.live_main(),"startup was not admitted after configuration/setup");
        const auto resident=scene.resident_sound();require_view(bool(resident),"startup lost resident driver");
        const auto capture=[&](const char* suffix) {
            const auto seed=scene.process_random_state();const auto cycles=resident->player().player().timers().cycles();
            const auto tick=scene.startup_scene() ? scene.startup_scene()->ticks() : 0;
            scene.repaint();const auto pixels=scene.frame().pixels;scene.repaint();
            require_view(pixels==scene.frame().pixels && scene.process_random_state()==seed &&
                resident->player().player().timers().cycles()==cycles &&
                (!scene.startup_scene() || scene.startup_scene()->ticks()==tick),"repaint consumed startup state/audio time");
            write_bmp((folder/(std::string(suffix)+".bmp")).string(),scene.frame());
        };
        scene.input(menu::Input::confirm);scene.input(menu::Input::cancel);
        require_view(scene.startup_scene() && !scene.live_main(),"menu actions escaped startup");capture("initial");
        unsigned ticks=0;const bool skip=index!=0 && index!=9;
        while(scene.startup_scene() && ticks<3000) {
            scene.advance(skip ? 0xffff : 0,false,false);++ticks;
            if(!phase && scene.startup_scene())require_view(!fs::exists(score_path),"score access/recreation preceded title completion");
        }
        require_view(ticks<3000 && logos==1 && completions==1 && title_loads==1 &&
            scene.resident().zunsoft_shown && scene.generation()==1 && scene.resident().random_seed_source==0,
            "first startup did not preserve logo/title/process boundaries");
        require_view(fs::is_regular_file(score_path) && fs::file_size(score_path)==1960,"startup did not create/reopen ten score partitions");
        if(phase)require_view(read(score_path)==old_score && scene.process_random_state()==startup_random,"host restart rekeyed valid scores");
        capture("menu");state<<"STARTUP "<<ticks<<' '<<startup_random<<' '<<scene.process_random_state()<<'\n';
        if(!phase && index==0) {
            scene.input(menu::Input::confirm);scene.input(menu::Input::confirm);scene.input(menu::Input::confirm);
            require_view(scene.live_main() && scene.generation()==2 && scene.resident_sound()==resident,"startup did not enter ordinary MAIN");
            for(unsigned frame=0;frame<1000 && !scene.main_state().game_over();++frame)scene.advance(0,false,false);
            require_view(scene.main_state().game_over(),"ordinary finite STD did not reach Game Over");capture("gameover");
            unsigned clock=0;
            while(scene.live_main() && clock<650) {
                ++clock;scene.advance(clock==114 ? 0x2000 : clock>=101 && clock<=109 ? shot::input_shot : 0,false,false);
            }
            require_view(scene.score_route() && scene.program()==application::Program::maine && scene.generation()==3,
                "ordinary Quit did not enter score-only MAINE");
            for(unsigned i=0;i<135;++i)scene.advance(0,false,false);
            require_view(scene.registration_scene() && !scene.registration_scene()->menu().editable(),"zero-score registration placement");
            scene.advance(0,false,false);scene.advance(0,false,false);scene.advance(0x2000,false,false);
            for(unsigned i=0;i<18;++i)scene.advance(0,false,false);
            require_view(scene.score_route()->verdict_scene(),"registration did not admit verdict");
            unsigned guard=0;
            while(scene.score_route()->verdict_scene()->status()!=verdict::Status::release && guard++<1000)scene.advance(shot::input_shot,false,false);
            require_view(guard<1000,"verdict release gate");
            cfg::HostStore changed(save);auto changed_options=changed.options();changed_options.lives=2;changed.save(changed_options,false);
            scene.advance(0,false,false);scene.advance(0,false,false);scene.advance(shot::input_shot,false,false);
            for(unsigned i=0;i<35 && scene.program()==application::Program::maine;++i)scene.advance(0,false,false);
            require_view(scene.program()==application::Program::op && scene.generation()==4 && scene.startup_scene() &&
                scene.resident_sound()==resident && scene.resident().zunsoft_shown && !scene.main_resources_alive(),"fresh OP startup/lifetimes");
            require_view(scene.resident().config.lives==2,"fresh OP did not reload physical configuration before title");
            const auto saved=read(score_path);const auto cycles=resident->player().player().timers().cycles();
            for(unsigned i=0;i<174;++i) {
                scene.advance(0xffff,false,false);require_view(scene.startup_scene(),"held key shortened fresh OP title");
            }
            scene.advance(0xffff,false,false);
            require_view(!scene.startup_scene() && logos==1 && completions==2 && title_loads==2 && scene.process_random_state()==1 &&
                read(score_path)==saved && resident->player().player().timers().cycles()>cycles,"fresh OP replayed logo/rekeyed score/reset audio");
            capture("fresh-op");state<<"FRESH 175 "<<scene.generation()<<' '<<scene.process_random_state()<<'\n';
        }
        scene.close_window();
        cfg::HostStore reopened(save);require_view(!reopened.setup_required() && reopened.options().bgm_mode==bgm &&
            reopened.options().se_mode==se,"OP exit did not persist setup/configuration");
        require_view(bool(events) && bool(state) && bool(pcm),"startup captures incomplete");
        std::cout<<"STARTUP "<<name<<" phase="<<phase<<" ticks="<<ticks<<" logos="<<logos<<" muted=1\n";
    }
}

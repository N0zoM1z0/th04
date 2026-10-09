// Actual native OP/menu/MAIN and a declared seeded registration child. These
// controls are muted CPU captures, not natural survival or original full pixels.
void run_resident_sound_checks(const PiImage& background,const CdgSheet& numerals,
    const CdgSheet& labels,const CdgSheet& cursors,const PiImage& selection_background,
    const CdgSheet& portraits,const MainAssets& assets,const std::string& destination) {
    namespace fs=std::filesystem;const fs::path directory(destination);
    require_view(assets.muted && assets.pmd_profile && !fs::exists(directory),"resident checks need an installed profile and fresh muted outputs");
    fs::create_directories(directory);
    for(unsigned bgm=0;bgm<3;++bgm)for(unsigned se=0;se<3;++se) {
        const unsigned character=(bgm+se)&1;const auto name=std::to_string(bgm)+"-"+std::to_string(se);
        const auto folder=directory/name;fs::create_directories(folder);
        auto input=assets;input.save_directory=(folder/"save").string();
        th04::portable::configuration::HostStore cfg(input.save_directory);cfg.complete_setup(std::uint8_t(bgm),std::uint8_t(se));cfg.save(cfg.options(),false);
        FrontEnd scene(background,numerals,labels,cursors,selection_background,portraits,&input);
        std::ofstream pcm(folder/"mixed.pcm",std::ios::binary),state(folder/"state.txt",std::ios::binary);
        std::uint64_t count=0;std::map<unsigned,std::uint64_t> generations;
        scene.set_stereo_observer([&](auto p,auto g,const auto& values){
            state<<"BLOCK "<<unsigned(p)<<' '<<g<<' '<<values.size()<<'\n';generations[g]+=values.size();count+=values.size();
            for(auto v:values)for(auto word:{v.left,v.right}){pcm.put(char(std::uint16_t(word)&255));pcm.put(char(std::uint16_t(word)>>8));}
        });
        scene.enable_configuration();scene.enable_registration();scene.advance(0,false,false);
        const auto resident=scene.resident_sound();require_view(bool(resident),"actual frontend omitted resident PMD");
        const auto effective=bgm==0 ? 0 : bgm==1 || assets.pmd_profile->board==th04::portable::pmd::Board::fm26 ? 1 : 2;
        require_view(scene.sound_runtime()->control().bgm==effective && scene.sound_runtime()->control().se==se,"actual profile/config mode detection");
        const auto before=resident->player().pcm().samples();scene.repaint();scene.repaint();
        require_view(resident->player().pcm().samples()==before,"repaint advanced resident clock");
        write_bmp((folder/"op.bmp").string(),scene.frame());
        while(scene.menu_state().selection()!=unsigned(menu::MainChoice::music_room))scene.input(menu::Input::down);
        scene.input(menu::Input::confirm);
        for(unsigned tick=0;scene.music_scene() && tick<300;++tick)scene.advance(tick%60==40 ? 0x2000 : tick==7 ? 0x1000 : 0,false,false);
        require_view(!scene.music_scene() && scene.generation()==1 && scene.resident_sound()==resident,"Music Room changed process/resident ownership");
        while(scene.menu_state().selection()!=unsigned(menu::MainChoice::game))scene.input(menu::Input::down);
        scene.input(menu::Input::confirm);if(character)scene.input(menu::Input::right);
        scene.input(menu::Input::confirm);scene.input(menu::Input::confirm);
        require_view(scene.live_main() && scene.generation()==2 && scene.resident_sound()==resident,"ordinary MAIN lost PMD lifetime");
        for(unsigned tick=0;tick<24;++tick)scene.advance(tick<12 ? shot::input_shot : 0x800,false,false);
        scene.repaint();write_bmp((folder/"main.bmp").string(),scene.frame());
        state<<"MAIN "<<+scene.sound_runtime()->control().bgm<<' '<<+scene.sound_runtime()->control().se<<' '<<resident->player().player().timers().cycles()<<'\n';
        // A separate declared child fixture covers score close/fresh OP while
        // retaining this application's real driver; it does not seed gameplay.
        scene.close_window();
        FrontEnd child(background,numerals,labels,cursors,selection_background,portraits,&input);
        child.enable_configuration();child.enable_registration();child.advance(0,false,false);
        const auto child_resident=child.resident_sound();
        child.seed_registration_fixture(character,1,1);
        require_view(child.program()==application::Program::maine && child.resident_sound()==child_resident && child.sound_runtime()->beeper().count==0,"MAINE must preserve PMD but initialize empty beeper");
        const auto clock=child_resident->player().player().timers().cycles();
        for(unsigned tick=0;child.program()==application::Program::maine && tick<300;++tick)child.advance(tick%12==7 ? 0x2000 : 0,false,false);
        require_view(child.program()==application::Program::op && child.generation()==4 && child.resident_sound()==child_resident && child_resident->player().player().timers().cycles()>clock,"score close/fresh OP reset resident clock");
        child.repaint();write_bmp((folder/"fresh-op.bmp").string(),child.frame());
        state<<"FRESH "<<child.generation()<<' '<<child_resident->player().player().timers().cycles()<<' '<<count<<'\n';
        require_view(count && generations[1] && generations[2] && bool(pcm) && bool(state),"resident captures incomplete");
        std::cout<<"RESIDENT_SOUND "<<name<<" character="<<character<<" samples="<<count<<" fresh_op=1 muted=1\n";
    }
    // Authored legal wait script, original music resources, real Ending and
    // Staff owners. It isolates the native consumer connection from full routes.
    for(bool active:{false,true}) {
        application::State app;menu::Options options;options.bgm_mode=active ? 2 : 0;options.se_mode=1;app.apply_options(options);app.start_normal(application::Playchar::reimu,application::ShotType::a);
        auto resident=std::make_shared<sound::ResidentPmd>(*assets.pmd_profile);
        sound::Timeline audio([&](const std::string& name)->std::optional<sound::Bytes>{auto key=name;for(auto& c:key)if(c>='a'&&c<='z')c=char(c-'a'+'A');const auto f=assets.sound_resources.find(key);return f==assets.sound_resources.end() ? std::nullopt : std::optional<sound::Bytes>{f->second};},{},{},resident);
        audio.enter(application::Program::main,app.generation(),options);audio.handle({sound::ActionKind::load,0x600,"st00"});audio.handle({sound::ActionKind::command,0});
        if(active) {
            for(unsigned i=0;resident->command(0x500)<3 && i<16;++i)audio.runtime()->advance(1000000000);
            require_view(resident->command(0x500)>=3,"previous real song did not establish stale-measure control");
        }
        auto pictures=assets.ending;pictures.scripts.clear();const std::string script="\\m,logo \\wm1,600\\$";pictures.scripts.emplace("_ED000.TXT",Bytes(script.begin(),script.end()));
        maine::Ending ending(app,{},application::EndSequence::good,pictures,[&]{audio.leave();},false,&audio);
        for(unsigned i=0;i<273;++i){auto owner=audio.runtime();sound::Refresh refresh(owner.get(),frame_period.count());ending.advance(0);}
        // wm first performs four timed text-box mask steps. Admit the wait
        // after those real scene requests, rather than assuming one advance.
        unsigned admission=0;
        while(ending.scene()->script().status()!=cutscene::Status::measure && admission<8) {
            auto owner=audio.runtime();sound::Refresh refresh(owner.get(),frame_period.count());
            ending.advance(0);++admission;
        }
        require_view(ending.scene()->script().status()==cutscene::Status::measure &&
                     (!active || resident->command(0x500)==0),"new song must start below wait goal");
        const auto cycle=resident->player().player().timers().cycles();
        for(unsigned i=0;i<100;++i)ending.advance(0);
        if(active)require_view(ending.scene()->script().status()==cutscene::Status::measure && resident->player().player().timers().cycles()==cycle,"time-free polling fabricated measures");
        unsigned ticks=0;
        while(ending.phase()!=maine::Phase::staff_roll_pending && ticks<1000){auto owner=audio.runtime();sound::Refresh refresh(owner.get(),frame_period.count());ending.advance(0);++ticks;}
        require_view(ending.phase()==maine::Phase::staff_roll_pending && (active ? ticks<500 && resident->command(0x500)>=1 : ticks==500),"real measure/inactive fallback wait differs");
        if(active) {
            for(unsigned i=0;resident->command(0x500)<7 && i<16;++i)audio.runtime()->advance(1000000000);
            require_view(resident->command(0x500)>=7,"Ending song did not establish STAFF stale-measure control");
            ending.start_staff_roll(assets.staff_roll);
            for(unsigned i=0;i<1500 && ending.staff_scene()->status()!=th04::portable::staff::Status::measure;++i){auto owner=audio.runtime();sound::Refresh refresh(owner.get(),frame_period.count());ending.advance(0);}
            require_view(ending.staff_scene()->status()==th04::portable::staff::Status::measure && resident->command(0x500)<3,"STAFF wait inherited prior song progress");
            for(unsigned i=0;i<1500 && ending.staff_scene()->status()==th04::portable::staff::Status::measure;++i){auto owner=audio.runtime();sound::Refresh refresh(owner.get(),frame_period.count());ending.advance(0);}
            require_view(ending.staff_scene()->status()!=th04::portable::staff::Status::measure && resident->command(0x500)>=3,"STAFF measure provider failed to resume");
        }
        std::ofstream(directory/(active ? "measure-active.txt" : "measure-off.txt"),std::ios::binary)<<ticks<<' '<<resident->command(0x500)<<' '<<resident->player().player().timers().cycles()<<'\n';
    }
}

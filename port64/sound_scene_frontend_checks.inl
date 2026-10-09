// Full-scene traces are separate from the existing MAIN-only replay API.
void attach_sound_scene_trace(FrontEnd& scene,std::ostream& out) {
    scene.set_sound_scene_observer([&scene,&out](const sound::SceneEvent& e) {
        const auto* runtime=scene.sound_runtime();require_view(runtime!=nullptr || e.kind==sound::SceneKind::leave,"sound owner absent at request");
        out<<int(e.kind)<<' '<<int(e.program)<<' '<<e.generation<<' '<<int(e.action.kind)<<' '
           <<e.action.value<<' '<<(e.action.name.empty() ? "-" : e.action.name)<<' '
           <<+e.options.bgm_mode<<' '<<+e.options.se_mode<<' '<<e.goal<<' '<<e.fallback;
        if(runtime) {
            const auto& state=runtime->control();
            out<<' '<<+state.bgm<<' '<<+state.se<<' '<<+state.midi_possible<<' '
               <<+state.interrupt_if_midi<<' '<<+state.playing<<' '<<+state.frame<<' ';
            constexpr char digits[]="0123456789abcdef";
            for(auto b:state.filename)out<<digits[b>>4]<<digits[b&15];
            out<<' '<<runtime->beeper().count;
        }
        out<<'\n';require_view(bool(out),"sound scene trace write");
    });
}

void run_sound_menu_checks(const PiImage& background,const CdgSheet& numerals,
    const CdgSheet& labels,const CdgSheet& cursors,const PiImage& selection_background,
    const CdgSheet& portraits,const MainAssets& assets,const std::string& destination) {
    namespace fs=std::filesystem;const fs::path directory(destination);
    require_view(!fs::exists(directory) && assets.muted,"sound menu controls require fresh muted outputs");
    fs::create_directories(directory);
    for(unsigned character=0;character<2;++character)for(unsigned paint=0;paint<2;++paint) {
        const auto location=directory/("c"+std::to_string(character)+"-paint"+std::to_string(paint));
        fs::create_directories(location);auto input=assets;input.save_directory=(location/"save").string();
        th04::portable::configuration::HostStore cfg(input.save_directory);
        cfg.complete_setup(2,2);cfg.save(cfg.options(),false);
        std::ofstream trace(location/"sound.txt",std::ios::binary);
        FrontEnd scene(background,numerals,labels,cursors,selection_background,portraits,&input);
        attach_sound_scene_trace(scene,trace);scene.enable_configuration();scene.enable_registration();
        require_view(scene.sound_runtime()->beeper().count==15 && scene.sound_runtime()->control().se==2,
            "fresh OP real EFS/config initialization");
        while(scene.menu_state().selection()!=unsigned(menu::MainChoice::options))scene.input(menu::Input::down);
        scene.input(menu::Input::confirm);
        while(scene.menu_state().selection()!=unsigned(menu::OptionChoice::sound_effects))scene.input(menu::Input::down);
        scene.input(menu::Input::left); // BEEP -> OFF; effective mode remains BEEP.
        require_view(scene.menu_state().options().se_mode==0 && scene.sound_runtime()->control().se==2,
            "TH04 SE-only option must defer mode determination");
        scene.input(menu::Input::up);scene.input(menu::Input::left);
        require_view(scene.sound_runtime()->control().se==0 && scene.sound_runtime()->beeper().count==15,
            "BGM restart must apply deferred SE without reloading EFS");
        scene.input(menu::Input::down);scene.input(menu::Input::right); // OFF -> BEEP.
        scene.input(menu::Input::up);scene.input(menu::Input::right);
        require_view(scene.sound_runtime()->control().se==2,"BGM restart must determine new SE mode");
        scene.input(menu::Input::cancel);
        for(unsigned visit=0;visit<2;++visit) {
            while(scene.menu_state().selection()!=unsigned(menu::MainChoice::music_room))scene.input(menu::Input::down);
            scene.input(menu::Input::confirm);
            for(unsigned tick=0;scene.music_scene() && tick<250;++tick)
                scene.advance(tick%60==40 ? 0x2000 : tick==7 ? 0x1000 : 0,false,paint!=0);
            require_view(!scene.music_scene() && scene.program()==application::Program::op && scene.generation()==1,
                "Music Room sound must retain OP generation");
        }
        while(scene.menu_state().selection()!=unsigned(menu::MainChoice::scores))scene.input(menu::Input::down);
        scene.input(menu::Input::confirm);
        for(unsigned tick=0;scene.ranking_scene() && tick<300;++tick)
            scene.advance(tick%60==40 ? 0x2000 : 0,false,paint!=0);
        require_view(!scene.ranking_scene() && scene.generation()==1,"Scores sound must return to retained OP");
        // Seeded MAINE child fixture: real registration/save/fresh OP, no
        // claim that the preceding normal or Extra gameplay was traversed.
        scene.seed_registration_fixture(character,character ? 4 : 1,1);
        require_view(scene.program()==application::Program::maine && scene.sound_runtime()->beeper().count==0,
            "MAINE inherited OP effects");
        for(unsigned tick=0;scene.program()==application::Program::maine && tick<300;++tick)
            scene.advance(tick%12==7 ? 0x2000 : 0,false,paint!=0);
        require_view(scene.program()==application::Program::op && scene.generation()==4 &&
            scene.sound_runtime()->beeper().count==15,"registration did not rebuild fresh OP audio");
        const auto before=scene.sound_runtime()->samples();scene.repaint();scene.repaint();
        require_view(scene.sound_runtime()->samples()==before,"repaint advanced OP audio");
        while(scene.menu_state().selection()!=unsigned(menu::MainChoice::game))scene.input(menu::Input::down);
        scene.input(menu::Input::confirm);if(character)scene.input(menu::Input::right);
        scene.input(menu::Input::confirm);scene.input(menu::Input::confirm);
        require_view(scene.live_main() && scene.sound_runtime()->beeper().count==15,"fresh OP failed second MAIN audio");
        scene.advance(0,false,paint!=0);
        std::cout<<"SOUND_SCENE c"<<character<<" paint="<<paint<<" retained_op=1 fresh_op=1 main=1 muted=1\n";
    }
}

void run_sound_option_checks(const PiImage& background,const CdgSheet& numerals,
    const CdgSheet& labels,const CdgSheet& cursors,const PiImage& selection_background,
    const CdgSheet& portraits,const MainAssets& assets,const std::string& destination) {
    namespace fs=std::filesystem;const fs::path directory(destination);fs::create_directories(directory);
    unsigned count=0;
    for(unsigned bgm=0;bgm<3;++bgm)for(unsigned se=0;se<3;++se)
    for(unsigned row:{3u,4u,6u,7u})for(unsigned key:{1u,2u,4u,8u,0x20u,0x2000u}) {
        const auto location=directory/std::to_string(count++);fs::create_directories(location);
        auto input=assets;input.save_directory=(location/"save").string();
        th04::portable::configuration::HostStore cfg(input.save_directory);
        cfg.complete_setup(std::uint8_t(bgm),std::uint8_t(se));cfg.save(cfg.options(),false);
        FrontEnd scene(background,numerals,labels,cursors,selection_background,portraits,&input);
        scene.enable_configuration();scene.enable_registration();
        while(scene.menu_state().selection()!=unsigned(menu::MainChoice::options))scene.input(menu::Input::down);
        scene.input(menu::Input::confirm);
        while(scene.menu_state().selection()!=row)scene.input(menu::Input::down);
        std::ofstream trace(location/"sound.txt",std::ios::binary);attach_sound_scene_trace(scene,trace);
        scene.input(key==1 ? menu::Input::up : key==2 ? menu::Input::down :
                    key==4 ? menu::Input::left : key==8 ? menu::Input::right : menu::Input::confirm);
        const auto& options=scene.menu_state().options();
        std::ofstream state(location/"case.txt",std::ios::binary);
        state<<bgm<<' '<<se<<' '<<row<<' '<<key<<' '<<+options.bgm_mode<<' '<<+options.se_mode<<'\n';
    }
    std::cout<<"SOUND_OPTIONS "<<count<<" actual OP option actions muted=1\n";
}

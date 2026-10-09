// Ordinary OP options/selection, real MAIN events and offline beeper samples.
void run_sound_checks(const PiImage& background,const CdgSheet& numerals,
    const CdgSheet& labels,const CdgSheet& cursors,const PiImage& selection_background,
    const CdgSheet& portraits,const MainAssets& assets,const std::string& destination) {
    namespace fs=std::filesystem;const fs::path directory(destination);
    require_view(!fs::exists(directory) && assets.muted && !assets.main_effects.empty(),"use fresh muted sound controls");
    fs::create_directories(directory);std::ofstream journal(directory/"trace.txt",std::ios::binary);
    struct Restore {std::streambuf* old;~Restore(){std::cout.rdbuf(old);}} restore{std::cout.rdbuf(journal.rdbuf())};
    Bytes standard{0,0,8};standard.insert(standard.end(),8,0);standard.push_back(9);
    standard.insert(standard.end(),8,16);standard.push_back(0);
    for(auto x:{1,9,0x10,128,1,0,0,0,6,100,0,0})standard.push_back(std::uint8_t(x));
    for(unsigned frame:{64u,2000u}) {
        standard.push_back(std::uint8_t(frame));standard.push_back(std::uint8_t(frame>>8));standard.insert(standard.end(),{1,0,0,12,0,20,255,0,0});
    }
    standard.insert(standard.end(),{0,0});const auto extent=standard.size()-2;
    standard[0]=std::uint8_t(extent);standard[1]=std::uint8_t(extent>>8);
    for(unsigned character=0;character<2;++character)for(unsigned profile=0;profile<3;++profile)for(unsigned paint=0;paint<2;++paint) {
        auto input=assets;input.standard=standard;const auto name="c"+std::to_string(character)+"-p"+std::to_string(profile)+"-paint"+std::to_string(paint);
        const auto out=directory/name;fs::create_directories(out);input.save_directory=(out/"save").string();
        std::ofstream records(out/"actions.txt",std::ios::binary),states(out/"states.txt",std::ios::binary),pcm(out/"samples.pcm",std::ios::binary);
        unsigned clock=0,updates=0,plays=0,waits=0;bool continued=false;
        FrontEnd scene(background,numerals,labels,cursors,selection_background,portraits,&input);
        scene.set_sound_observer([&](const sound::Action& a){records<<clock<<' '<<int(a.kind)<<' '<<a.value<<' '<<(a.name.empty()?"-":a.name)<<'\n';updates+=a.kind==sound::ActionKind::update;plays+=a.kind==sound::ActionKind::play;},
            [&](const std::vector<std::int16_t>& values){for(auto sample:values){const char bytes[2]{char(std::uint16_t(sample)&255),char(std::uint16_t(sample)>>8)};pcm.write(bytes,2);}});
        if(profile==2)scene.enable_registration();
        // Actual OP Options: SE FM -> BEEP. Game Over uses one ordinary life.
        for(unsigned n=0;n<3;++n)scene.input(menu::Input::down);
        scene.input(menu::Input::confirm);scene.input(menu::Input::down);
        if(profile==2){scene.input(menu::Input::left);scene.input(menu::Input::left);}
        for(unsigned n=0;n<3;++n)scene.input(menu::Input::down);
        scene.input(menu::Input::left);
        scene.input(menu::Input::cancel);for(unsigned n=0;n<3;++n)scene.input(menu::Input::up);
        scene.input(menu::Input::confirm);if(character)scene.input(menu::Input::right);
        scene.input(menu::Input::confirm);scene.input(menu::Input::confirm);
        require_view(scene.live_main() && scene.resident().config.se_mode==2 && scene.sound_runtime()->beeper().count==15,"MAIN EFS actual resource/options handoff");
        const auto& initial=scene.sound_runtime()->control();states<<"0 "<<scene.main_state().frames()<<' '<<+initial.se<<' '<<+initial.playing<<' '<<+initial.frame<<" 0 0 0 0\n";
        for(clock=1;clock<=700;++clock) {
            auto& main=scene.main_state();const auto before=main.frames();const bool blocked=main.game_over() && !main.game_over()->finished();
            const auto sound_before=scene.sound_runtime()->control();const auto samples_before=scene.sound_runtime()->samples();const auto update_before=updates;
            std::uint16_t keys=profile==0 ? shot::input_shot : profile==1 && clock<180 ? 0x800 : 0;
            if(profile==2 && main.game_over()) {
                const auto phase=main.game_over()->phase();
                if(phase==gameover::Phase::press || phase==gameover::Phase::menu)keys=clock%8 ? 0 : shot::input_shot;
            }
            records<<clock<<" T "<<std::uint64_t(frame_period.count())*scene.slowdown()<<" -\n";
            scene.advance(keys,false,paint!=0);
            require_view(scene.live_main(),"bounded sound fixture left MAIN");
            const auto* runtime=scene.sound_runtime();const auto& s=runtime->control();const auto& b=runtime->beeper();
            if(blocked && main.frames()==before) {
                ++waits;require_view(updates==update_before && s.playing==sound_before.playing && s.frame==sound_before.frame && runtime->samples()>samples_before,
                    "Game Over must freeze ordinary SE while IRQ time continues");
            }
            if(profile==2 && !main.game_over() && waits)continued=true;
            states<<clock<<' '<<main.frames()<<' '<<+s.se<<' '<<+s.playing<<' '<<+s.frame<<' '<<runtime->samples()<<' '<<b.phase<<' '<<b.selected<<' '<<b.active<<'\n';
            records<<clock<<" E 0 -\n";
            if(clock%17==0) {
                const auto samples=runtime->samples();const auto events=updates+plays;
                scene.repaint();const auto first=scene.frame().pixels;scene.repaint();
                require_view(runtime->samples()==samples && updates+plays==events && scene.frame().pixels==first,"repaint changed sound state");
            }
        }
        require_view(plays>0 && updates>0 && (!profile || scene.main_state().life().bombs_used==unsigned(profile==1)),"ordinary sound events missing");
        if(profile==2)require_view(waits>100 && continued,"ordinary sound Game Over/Continue did not finish");
        require_view(bool(records) && bool(states) && bool(pcm),"sound fixture output write");
        std::cout<<name<<" updates="<<updates<<" plays="<<plays<<" waits="<<waits<<" samples="<<scene.sound_runtime()->samples()<<'\n';
    }
}

// Real OP Extra/STD/dialog/Mugetsu dispatch. Long controls explicitly suppress
// player-hit consumption; shooting and X use the genuine MAIN lifecycle.
void run_mugetsu_checks(const PiImage& background,const CdgSheet& numerals,
    const CdgSheet& labels,const CdgSheet& cursors,const PiImage& selection_background,
    const CdgSheet& portraits,const MainAssets& assets,const std::string& output) {
    namespace fs=std::filesystem;const fs::path directory(output);
    require_view(assets.muted && !fs::exists(directory),"Mugetsu checks need muted/fresh output");fs::create_directories(directory);
    for(unsigned character=0;character<2;++character)for(unsigned shot_type=0;shot_type<2;++shot_type)
        for(unsigned shooting=0;shooting<2;++shooting)for(unsigned paint=0;paint<2;++paint) {
        const auto name=std::to_string(character)+"-"+std::to_string(shot_type)+"-"+std::to_string(shooting)+"-"+std::to_string(paint);
        FrontEnd scene(background,numerals,labels,cursors,selection_background,portraits,&assets,gameplay::Mode::actor_control);
        scene.retain_gengetsu_gate_for_control();scene.unlock_extra_for_control();scene.input(menu::Input::down);scene.input(menu::Input::confirm);
        if(character)scene.input(menu::Input::right);
        scene.input(menu::Input::confirm);
        if(shot_type)scene.input(menu::Input::down);
        scene.input(menu::Input::confirm);
        require_view(unsigned(scene.resident().playchar)==character && unsigned(scene.resident().shot_type)==shot_type,
            "Mugetsu fixture selected wrong character/shot type");
        std::ofstream trace(directory/(name+".txt"),std::ios::binary);
        const auto generation=scene.generation();unsigned waits=0,dialog_ticks=0,battle_ticks=0,hit_frames=0,wing_frames=0,bomb_frames=0;
        bool started=false,held_release=false,held_press=false,bomb_requested=false;unsigned phases=0;std::uint8_t previous=0;
        const auto capture=[&](const std::string& suffix) {
            scene.repaint();write_bmp((directory/(name+"-"+suffix+".bmp")).string(),scene.frame());
            const auto pixels=scene.frame().pixels;const auto rng=scene.main_state().random_cursor();const auto frames=scene.main_state().frames();
            const auto draw_count=scene.main_state().boss_draws().size();const auto life=scene.main_state().life().bomb_frame;
            scene.repaint();require_view(scene.frame().pixels==pixels && scene.main_state().frames()==frames && scene.main_state().random_cursor()==rng &&
                scene.main_state().boss_draws().size()==draw_count && scene.main_state().life().bomb_frame==life,"Mugetsu repaint advanced retained owners");
        };
        for(unsigned tick=0;tick<28000 && !scene.gengetsu_dialog_pending();++tick) {
            const auto before=scene.main_state().frames();const auto cursor=scene.main_state().random_cursor();
            const bool blocked=scene.dialog_active();std::uint16_t held=0;
            if(blocked) {
                ++dialog_ticks;
                if(scene.dialog_status()==dialog::Status::release) {
                    ++waits;
                    if(!held_release) {
                        held_release=true;const auto offset=scene.dialog_offset();
                        for(unsigned i=0;i<10;++i)scene.advance(1,false,paint!=0);
                        require_view(scene.main_state().frames()==before && scene.main_state().random_cursor()==cursor && scene.dialog_offset()==offset && scene.dialog_status()==dialog::Status::release,"Extra held release skipped wait or resumed MAIN");
                        capture("release");
                    }
                } else if(scene.dialog_status()==dialog::Status::press) {
                    if(!held_press) {
                        held_press=true;const auto offset=scene.dialog_offset();
                        for(unsigned i=0;i<7;++i)scene.advance(0,false,paint!=0);
                        require_view(scene.main_state().frames()==before && scene.main_state().random_cursor()==cursor && scene.dialog_offset()==offset && scene.dialog_status()==dialog::Status::press,"Extra press wait resumed MAIN without action");
                        capture("press");
                    }
                    held=0x1000;
                }
            } else if(scene.main_state().mugetsu_active()) {
                held=shooting ? shot::input_shot : 0;
                const int dx=scene.main_state().boss_snapshot().position.current.x-scene.main_state().player().position().current.x;
                if(shooting && std::abs(dx)>32)held|=dx<0 ? player::left : player::right;
                if(shooting && !bomb_requested && scene.main_state().boss_snapshot().phase==2 && scene.main_state().boss_snapshot().phase_frame>=32) {
                    held|=0x800;bomb_requested=true;
                }
            }
            scene.advance(held,false,paint!=0);
            const auto& state=scene.main_state();
            if(blocked && scene.dialog_active())require_view(state.frames()==before && state.random_cursor()==cursor,"Extra dialog advanced simulation/RNG");
            if(!state.mugetsu_active())continue;
            require_view(scene.mugetsu_resources_valid() && !scene.dialog_active() && !scene.post_dialog() &&
                !state.next_stage_requested() && !state.good_ending_requested() && !state.bad_ending_requested() &&
                !state.midboss_state().active && scene.resource_stage()==6,"Mugetsu dispatched stale owner/resources/departure");
            if(state.frames()!=before)++battle_ticks;
            for(const auto& e:state.orange_events())if(e.type==orange::EventType::sound && e.value==4)++hit_frames;
            if(std::any_of(state.boss_draws().begin(),state.boss_draws().end(),[](const auto& d){return d.pattern_or_radius==136;}))++wing_frames;
            if(state.bomb_frame().active)++bomb_frames;
            const auto phase=state.boss_snapshot().phase;
            const bool boundary=!started || phase!=previous;
            if(boundary || battle_ticks%256==0) {
                trace<<state.frames()<<' '<<+phase<<' '<<state.boss_snapshot().phase_frame<<' '<<state.boss_snapshot().hp<<' '
                    <<state.boss_snapshot().position.current.x<<' '<<state.random_cursor()<<' '<<scene.process_random_state()<<' '
                    <<state.awarded_score_units()<<' '<<+state.mugetsu()->snapshot().cycle<<' '<<+state.mugetsu()->snapshot().bomb_invincibility<<' '
                    <<state.boss_draws().size()<<' '<<hit_frames<<' '<<wing_frames<<' '<<bomb_frames<<'\n';
                if(boundary){++phases;capture("phase"+std::to_string(phase));}
            }
            if(!started) {
                started=true;require_view(scene.dialog_offset()==987 && state.frames()==11197,"Extra first dialog lost its retained cursor or gate frame");
                for(const auto& e:scene.completed_dialog_events()) {
                    trace<<"dialog "<<int(e.kind)<<' '<<e.a<<' '<<e.b<<' '<<e.c<<' '<<e.d<<' '<<(e.name.empty() ? "-" : e.name)<<'\n';
                }
                for(const auto& e:scene.extra_resource_events())trace<<"resource "<<int(e.kind)<<' '<<e.slot<<' '<<(e.name.empty() ? "-" : e.name)<<' '<<e.image<<'\n';
            }
            previous=phase;
        }
        const auto& state=scene.main_state();
        require_view(started && scene.gengetsu_dialog_pending() && phases==10 && waits && held_release && held_press && battle_ticks>1000 &&
            (!shooting || (hit_frames && wing_frames && bomb_frames==227 && state.life().bombs_used==1)),"Mugetsu real dialog/battle lifecycle incomplete");
        const auto frames=state.frames(),rng=scene.process_random_state();const auto cursor=state.random_cursor();scene.repaint();const auto pixels=scene.frame().pixels;
        for(unsigned i=0;i<20;++i)scene.advance(0x800|shot::input_shot,false,paint!=0);
        scene.repaint();require_view(state.frames()==frames && scene.process_random_state()==rng && state.random_cursor()==cursor &&
            scene.generation()==generation && scene.frame().pixels==pixels,"Gengetsu dialog gate repeated Mugetsu or ordinary departure");
        trace<<"pending "<<frames<<' '<<battle_ticks<<' '<<dialog_ticks<<' '<<hit_frames<<' '<<wing_frames<<' '<<bomb_frames<<' '
            <<scene.dialog_offset()<<' '<<rng<<' '<<cursor<<'\n';
        std::cout<<"Mugetsu actor-control "<<name<<" frames="<<frames<<" battle="<<battle_ticks<<" hits="<<hit_frames<<" Bomb="<<bomb_frames<<" frontier=gengetsu_dialog_pending\n";
    }
}

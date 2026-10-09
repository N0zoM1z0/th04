// Real OP/Extra/retained first and second dialogues, Mugetsu and Gengetsu.
// These long controls suppress player hit consumption and adapt the unlock bit.
void run_gengetsu_checks(const PiImage& background,const CdgSheet& numerals,
    const CdgSheet& labels,const CdgSheet& cursors,const PiImage& selection_background,
    const CdgSheet& portraits,const MainAssets& assets,const std::string& output,bool complete_extra=false,bool maine_extra=false) {
    namespace fs=std::filesystem;const fs::path directory(output);
    require_view(assets.muted && !fs::exists(directory),"Gengetsu checks require muted/fresh output");fs::create_directories(directory);
    for(unsigned character=0;character<2;++character)for(unsigned shot_type=0;shot_type<2;++shot_type)
        for(unsigned shooting=complete_extra ? 1u : 0u;shooting<2;++shooting)for(unsigned paint=0;paint<2;++paint) {
        const auto name=std::to_string(character)+"-"+std::to_string(shot_type)+"-"+std::to_string(shooting)+"-"+std::to_string(paint);
        auto input=assets;
        if(maine_extra)input.save_directory=(directory/name/"save").string();
        FrontEnd scene(background,numerals,labels,cursors,selection_background,portraits,&input,gameplay::Mode::actor_control);
        if(maine_extra)scene.enable_registration();
        if(!complete_extra)scene.retain_extra_final_gate_for_control();
        scene.unlock_extra_for_control();scene.input(menu::Input::down);scene.input(menu::Input::confirm);
        if(character)scene.input(menu::Input::right);
        scene.input(menu::Input::confirm);if(shot_type)scene.input(menu::Input::down);scene.input(menu::Input::confirm);
        require_view(unsigned(scene.resident().playchar)==character && unsigned(scene.resident().shot_type)==shot_type,"Gengetsu controls selected wrong character/shot");
        std::ofstream trace(directory/(name+".txt"),std::ios::binary);
        const auto generation=scene.generation();std::array<bool,2> release{},press{},begun{},bomb{};
        std::array<unsigned,2> phases{},battle{},dialog_ticks{},hits{},bomb_frames{};
        unsigned wave_frames=0,laser_frames=0,column_frames=0;bool wave_capture=false,column_capture=false;
        unsigned previous_phase=999,previous_owner=999;
        const auto capture=[&](const std::string& suffix) {
            scene.repaint();write_bmp((directory/(name+"-"+suffix+".bmp")).string(),scene.frame());
            const auto pixels=scene.frame().pixels;const auto frames=scene.main_state().frames();
            const auto cursor=scene.main_state().random_cursor();const auto clock=scene.main_state().boss_snapshot().phase_frame;
            const auto angle=scene.main_state().boss_snapshot().angle;const auto flash=scene.main_state().gengetsu_active() ? scene.main_state().gengetsu()->snapshot().flash : 0;
            scene.repaint();require_view(pixels==scene.frame().pixels && frames==scene.main_state().frames() && cursor==scene.main_state().random_cursor() &&
                clock==scene.main_state().boss_snapshot().phase_frame && angle==scene.main_state().boss_snapshot().angle &&
                flash==(scene.main_state().gengetsu_active() ? scene.main_state().gengetsu()->snapshot().flash : 0),"Gengetsu repaint mutated state/RNG/foreground");
        };
        for(unsigned tick=0;tick<70000 && !scene.main_state().extra_final_dialog_pending();++tick) {
            const auto before=scene.main_state().frames();const auto cursor=scene.main_state().random_cursor();
            const bool blocked=scene.dialog_active();const unsigned dialog_owner=scene.main_state().mugetsu_active() ? 1 : 0;
            std::uint16_t held=0;
            if(blocked) {
                ++dialog_ticks[dialog_owner];
                if(scene.dialog_status()==dialog::Status::release && !release[dialog_owner]) {
                    release[dialog_owner]=true;const auto offset=scene.dialog_offset();
                    for(unsigned i=0;i<10;++i)scene.advance(shot::input_shot,false,paint!=0);
                    require_view(scene.main_state().frames()==before && scene.main_state().random_cursor()==cursor && scene.dialog_offset()==offset && scene.dialog_status()==dialog::Status::release,"Extra held release skipped wait");
                    capture("release"+std::to_string(dialog_owner));
                } else if(scene.dialog_status()==dialog::Status::press) {
                    if(!press[dialog_owner]) {
                        press[dialog_owner]=true;const auto offset=scene.dialog_offset();
                        for(unsigned i=0;i<7;++i)scene.advance(0,false,paint!=0);
                        require_view(scene.main_state().frames()==before && scene.main_state().random_cursor()==cursor && scene.dialog_offset()==offset && scene.dialog_status()==dialog::Status::press,"Extra press wait advanced MAIN");
                        capture("press"+std::to_string(dialog_owner));
                    }
                    held=shot::input_shot;
                }
            } else if(scene.main_state().boss_active()) {
                held=shooting ? shot::input_shot : 0;const unsigned owner=scene.main_state().gengetsu_active() ? 1 : 0;
                const int dx=scene.main_state().boss_snapshot().position.current.x-scene.main_state().player().position().current.x;
                if(shooting && std::abs(dx)>32)held|=dx<0 ? player::left : player::right;
                if(shooting && !bomb[owner] && scene.main_state().boss_snapshot().phase==2 && scene.main_state().boss_snapshot().phase_frame>=32) {held|=0x800;bomb[owner]=true;}
            }
            scene.advance(held,false,paint!=0);const auto& state=scene.main_state();
            if(blocked && scene.dialog_active())require_view(state.frames()==before && state.random_cursor()==cursor,"Extra dialogue repeated suspended MAIN prefix");
            if(scene.dialog_active() || (!state.mugetsu_active() && !state.gengetsu_active()))continue;
            const unsigned owner=state.gengetsu_active() ? 1 : 0;const auto& boss=state.boss_snapshot();
            require_view((owner ? scene.gengetsu_resources_valid() : scene.mugetsu_resources_valid()) && !state.next_stage_requested() &&
                !state.good_ending_requested() && !state.bad_ending_requested() && !state.midboss_state().active && scene.resource_stage()==6 && scene.generation()==generation,"Extra owner/resource/departure mismatch");
            if(state.frames()!=before)++battle[owner];
            for(const auto& e:state.orange_events())if(e.type==orange::EventType::sound && e.value==4)++hits[owner];
            if(state.bomb_frame().active)++bomb_frames[owner];
            if(!begun[owner]) {
                begun[owner]=true;require_view(scene.dialog_offset()==(owner ? 1736u : 987u),"Extra retained dialogue cursor changed");
                if(owner)require_view(boss.phase==0 && boss.phase_frame==0 && boss.position.current.x==3072 && boss.position.current.y==1536 && boss.additional[0]==1,"Gengetsu initial update preceded the resumed suffix");
                for(const auto& e:scene.completed_dialog_events())trace<<"dialog"<<owner<<' '<<int(e.kind)<<' '<<e.a<<' '<<e.b<<' '<<e.c<<' '<<e.d<<' '<<(e.name.empty() ? "-" : e.name)<<'\n';
            }
            if(owner) {
                const auto& draws=state.gengetsu()->draws();
                const bool wave=std::any_of(draws.begin(),draws.end(),[](const auto& d){return d.kind==11;});
                if(wave){++wave_frames;if(!wave_capture){capture("wave");wave_capture=true;}}
                if(std::any_of(draws.begin(),draws.end(),[](const auto& d){return d.kind==7;}))++laser_frames;
                if(boss.phase==5 && boss.mode==1 && boss.phase_frame>=32 && boss.phase_frame<96){++column_frames;if(!column_capture){capture("columns");column_capture=true;}}
            }
            const bool boundary=owner!=previous_owner || boss.phase!=previous_phase;
            if(boundary || battle[owner]%256==0) {
                trace<<"state "<<owner<<' '<<state.frames()<<' '<<+boss.phase<<' '<<boss.phase_frame<<' '<<boss.hp<<' '<<boss.position.current.x<<' '<<boss.position.current.y<<' '<<+boss.mode<<' '<<+boss.angle<<' '
                    <<state.random_cursor()<<' '<<scene.process_random_state()<<' '<<state.awarded_score_units()<<' '<<hits[owner]<<' '<<bomb_frames[owner]<<' '<<wave_frames<<' '<<laser_frames<<' '<<column_frames<<'\n';
                if(boundary){++phases[owner];capture("owner"+std::to_string(owner)+"-phase"+std::to_string(boss.phase));}
            }
            previous_owner=owner;previous_phase=boss.phase;
        }
        const auto& state=scene.main_state();
        require_view(begun[0] && begun[1] && state.extra_final_dialog_pending() && phases[0]==10 && phases[1]==12 && release[0] && release[1] && press[0] && press[1] && wave_frames && laser_frames && column_frames,"Gengetsu full actor sequence or dialogue waits incomplete");
        require_view(!shooting || (hits[0] && hits[1] && bomb_frames[0]==227 && bomb_frames[1]==227 && state.life().bombs_used==2),"Gengetsu shot/Bomb integration incomplete");
        for(const auto& e:scene.extra_resource_events())trace<<"resource "<<int(e.kind)<<' '<<e.slot<<' '<<(e.name.empty() ? "-" : e.name)<<' '<<e.image<<'\n';
        const auto frames=state.frames(),process=scene.process_random_state();const auto cursor=state.random_cursor();scene.repaint();const auto pixels=scene.frame().pixels;
        trace<<"pending "<<frames<<' '<<battle[0]<<' '<<battle[1]<<' '<<dialog_ticks[0]<<' '<<dialog_ticks[1]<<' '<<hits[0]<<' '<<hits[1]<<' '<<bomb_frames[0]<<' '<<bomb_frames[1]<<' '<<scene.dialog_offset()<<' '<<process<<' '<<cursor<<' '<<wave_frames<<' '<<laser_frames<<' '<<column_frames<<'\n';
        if(complete_extra) {
            unsigned final_wait_ticks=0,clears=0,completed=0;bool final_release=false,final_press=false;
            const auto graze=scene.resident().graze;
            const auto stage_graze=state.bullets().snapshot().graze;
            scene.advance(shot::input_shot,false,paint!=0);
            require_view(scene.dialog_active() && state.extra_final_dialog_blocked() && state.frames()==frames,
                         "third dialogue did not stop after its real MAIN prefix");
            require_view(scene.resident().graze==static_cast<std::uint16_t>(graze+stage_graze),"third dialogue graze publication differs");
            const auto frozen_cursor=state.random_cursor();
            for(unsigned tick=0;tick<2000 && !state.extra_ending_requested();++tick) {
                const auto before=state.frames();std::uint16_t held=0;
                if(scene.dialog_active()) {
                    ++final_wait_ticks;
                    if(scene.dialog_status()==dialog::Status::release && !final_release) {
                        final_release=true;const auto offset=scene.dialog_offset();
                        for(unsigned i=0;i<10;++i)scene.advance(shot::input_shot,false,paint!=0);
                        require_view(state.frames()==frames && state.random_cursor()==frozen_cursor && scene.dialog_offset()==offset && scene.dialog_status()==dialog::Status::release,"third dialogue held-release advanced MAIN");
                        capture("release2");
                    } else if(scene.dialog_status()==dialog::Status::press) {
                        if(!final_press) {
                            final_press=true;const auto offset=scene.dialog_offset();
                            for(unsigned i=0;i<7;++i)scene.advance(0,false,paint!=0);
                            require_view(state.frames()==frames && state.random_cursor()==frozen_cursor && scene.dialog_offset()==offset && scene.dialog_status()==dialog::Status::press,"third dialogue press wait advanced MAIN");
                            capture("press2");
                        }
                        held=shot::input_shot;
                    }
                }
                scene.advance(held,false,paint!=0);
                if(state.frames()!=before) {
                    ++completed;
                    for(const auto& e:state.orange_events())if(e.type==orange::EventType::stage_bonus)++clears;
                    if(completed==1) {
                        require_view(state.boss_snapshot().phase_frame==1 && state.clear_bonus() && !scene.dialog_active() && scene.dialog_offset()==1961,"third dialogue resumed an incorrect caller suffix");
                        for(const auto& e:scene.completed_dialog_events())trace<<"dialog2 "<<int(e.kind)<<' '<<e.a<<' '<<e.b<<' '<<e.c<<' '<<e.d<<' '<<(e.name.empty() ? "-" : e.name)<<'\n';
                        capture("all-clear");
                    }
                }
                if(scene.dialog_active())require_view(state.frames()==frames && state.random_cursor()==frozen_cursor,"third dialogue repeated MAIN prefix");
                require_view(!state.next_stage_requested() && !state.good_ending_requested() && !state.bad_ending_requested() && scene.generation()==generation,"Extra clear took an ordinary Ending or departure");
            }
            require_view(state.extra_ending_requested() && state.boss_snapshot().phase_frame==416 && completed==416 && clears==1 && final_release && final_press,"Extra clear/416 nonreturning exit incomplete");
            require_view(scene.resident().graze==static_cast<std::uint16_t>(graze+stage_graze),"third dialogue repeated graze publication");
            capture("end-extra");const auto final_frames=state.frames();const auto final_cursor=state.random_cursor();const auto final_process=scene.process_random_state();
            scene.repaint();const auto final_pixels=scene.frame().pixels;
            if(!maine_extra)for(unsigned tick=0;tick<20;++tick)scene.advance(0x800|shot::input_shot,false,paint!=0);
            scene.repaint();require_view(state.frames()==final_frames && state.random_cursor()==final_cursor && scene.process_random_state()==final_process && scene.frame().pixels==final_pixels,"end-extra request repeated MAIN suffix");
            for(const auto& e:scene.extra_resource_events())trace<<"resource3 "<<int(e.kind)<<' '<<e.slot<<' '<<(e.name.empty() ? "-" : e.name)<<' '<<e.image<<'\n';
            trace<<"extra_clear "<<final_frames<<' '<<completed<<' '<<clears<<' '<<final_wait_ticks<<' '<<scene.dialog_offset()<<' '<<scene.resident().graze<<' '<<state.score().score_delta<<' '<<state.awarded_score_units()<<' '<<final_process<<' '<<final_cursor<<'\n';
            if(maine_extra)run_extra_maine_tail(scene,directory,name,paint!=0,trace);
        } else {
            for(unsigned i=0;i<20;++i)scene.advance(0x800|shot::input_shot,false,paint!=0);
            scene.repaint();require_view(state.frames()==frames && scene.process_random_state()==process && state.random_cursor()==cursor && scene.frame().pixels==pixels,"final Extra dialogue gate repeated simulation");

        }
        std::cout<<"Gengetsu actor-control "<<name<<" frames="<<frames<<" battles="<<battle[0]<<','<<battle[1]<<(maine_extra ? " frontier=fresh_op_second_main" : complete_extra ? " frontier=end_extra_pending" : " frontier=extra_final_dialog_pending")<<std::endl;
    }
}

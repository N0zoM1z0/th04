// Diagnostic unlock and actor-only controls are explicit. These run real Extra
// archive STD, resources and the complete timed midboss through the frontend;
// player-hit acceptance and the two Extra bosses remain separate requirements.
void run_extra_checks(const PiImage& background,const CdgSheet& numerals,
    const CdgSheet& labels,const CdgSheet& cursors,const PiImage& selection_background,
    const CdgSheet& portraits,const MainAssets& assets,const std::string& output) {
    namespace fs=std::filesystem;const fs::path directory(output);
    require_view(assets.muted && !fs::exists(directory),"Extra checks need muted/fresh output");
    fs::create_directories(directory);
    for(unsigned character=0;character<2;++character)for(unsigned shot=0;shot<2;++shot)
        for(unsigned paint=0;paint<2;++paint) {
        const auto name=std::to_string(character)+"-"+std::to_string(shot)+"-"+std::to_string(paint);
        FrontEnd scene(background,numerals,labels,cursors,selection_background,portraits,&assets,gameplay::Mode::actor_control);
        scene.retain_extra_gate_for_control();scene.unlock_extra_for_control();scene.input(menu::Input::down);scene.input(menu::Input::confirm);
        if(character)scene.input(menu::Input::right);
        scene.input(menu::Input::confirm);
        if(shot)scene.input(menu::Input::down);
        scene.input(menu::Input::confirm);
        require_view(unsigned(scene.resident().playchar)==character && unsigned(scene.resident().shot_type)==shot && scene.extra_resources_valid() && scene.resident().stage==6 && scene.resident().credit_lives==3 && scene.resident().credit_bombs==2,"Extra selected wrong character/shot/resources");
        std::ofstream trace(directory/(name+".txt"),std::ios::binary);
        const auto generation=scene.generation();unsigned active_ticks=0,drops=0,draws=0,changes=0,extend_edges=0;
        std::uint8_t previous=0;bool activated=false,departed=false;
        for(unsigned tick=0;tick<12000 && !scene.extra_boss_pending();++tick) {
            const auto before=scene.main_state().frames();scene.advance(0,false,paint!=0);
            const auto& state=scene.main_state();const auto& mid=state.midboss_state();
            if(state.frames()==before)continue;
            if(mid.active) {activated=true;++active_ticks;draws+=unsigned(state.midboss_draws().size());}
            else if(activated)departed=true;
            for(const auto& e:state.midboss_events())if(e.type==th04::portable::midboss::EventType::item)++drops;
            require_view(!state.boss_active() && state.extra_setup() && scene.extra_resources_valid(),"Extra dispatched ordinary boss/resources");
            if(state.bullets().snapshot().clear_time==20 && state.bullet_render_clear()==0)++extend_edges;
            const bool boundary=mid.phase!=previous;
            if(boundary || state.frames()==1 || state.frames()==5400 || state.frames()==5401 ||
               state.frames()%256==0 || (!mid.active && activated && !departed)) {
                if(boundary)++changes;
                trace<<state.frames()<<' '<<unsigned(mid.phase)<<' '<<mid.phase_frame<<' '<<mid.hp<<' '
                    <<mid.position.current.x<<' '<<mid.position.current.y<<' '<<mid.position.previous.x<<' '<<mid.position.previous.y<<' '
                    <<mid.position.velocity.x<<' '<<unsigned(mid.unused_angle)<<' '<<mid.active<<' '<<state.random_cursor()<<' '
                    <<scene.process_random_state()<<' '<<state.awarded_score_units()<<' '<<drops<<' '<<draws<<' '<<extend_edges<<'\n';
                if(boundary || state.frames()==1 || state.frames()==5401) {
                    scene.repaint();write_bmp((directory/(name+"-"+std::to_string(state.frames())+".bmp")).string(),scene.frame());
                    const auto pixels=scene.frame().pixels;const auto cursor=state.random_cursor();scene.repaint();
                    require_view(scene.frame().pixels==pixels && state.random_cursor()==cursor,"Extra repaint advanced state");
                }
            }
            previous=mid.phase;
        }
        require_view(scene.extra_boss_pending() && activated && departed && changes==6 && drops==9 && active_ticks>2500 && draws>2400 && extend_edges,"Extra waves/midboss/drop/exit schedule incomplete");
        const auto frames=scene.main_state().frames(),rng=scene.process_random_state();const auto cursor=scene.main_state().random_cursor();
        scene.repaint();const auto pixels=scene.frame().pixels;
        for(unsigned i=0;i<20;++i)scene.advance(1,false,paint!=0);
        scene.repaint();require_view(scene.main_state().frames()==frames && scene.process_random_state()==rng && scene.main_state().random_cursor()==cursor && scene.generation()==generation && scene.frame().pixels==pixels,"Extra pending Boss gate repeated simulation");
        write_bmp((directory/(name+"-pending.bmp")).string(),scene.frame());
        trace<<"pending "<<frames<<' '<<active_ticks<<' '<<drops<<' '<<draws<<' '<<rng<<' '<<cursor<<' '<<extend_edges<<'\n';
        std::cout<<"Extra actor-control "<<name<<" frames="<<frames<<" midboss_ticks="<<active_ticks<<" drops="<<drops<<" frontier=mugetsu_dialog_pending\n";
    }
    // Ordinary lifecycle also enters the same real Extra resource/STD path.
    // This short smoke makes no all-stage/player survival assertion.
    for(unsigned character=0;character<2;++character) {
        FrontEnd scene(background,numerals,labels,cursors,selection_background,portraits,&assets);
        scene.retain_extra_gate_for_control();scene.unlock_extra_for_control();scene.input(menu::Input::down);scene.input(menu::Input::confirm);
        if(character)scene.input(menu::Input::right);
        scene.input(menu::Input::confirm);scene.input(menu::Input::confirm);
        require_view(unsigned(scene.resident().playchar)==character,"ordinary Extra fixture selected wrong character");
        for(unsigned tick=0;tick<120;++tick)scene.advance(tick%8<4 ? 1 : 2,false,false);
        require_view(scene.main_state().mode()==gameplay::Mode::ordinary && scene.main_state().frames()==120 && scene.extra_resources_valid(),"ordinary Extra startup failed");
        scene.repaint();write_bmp((directory/("ordinary-"+std::to_string(character)+".bmp")).string(),scene.frame());
    }
}

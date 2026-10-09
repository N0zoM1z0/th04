// Continue the actual Extra actor-control route at its real end_extra request.
void run_extra_maine_tail(FrontEnd& scene,const std::filesystem::path& directory,
                         const std::string& name,bool paint,std::ostream& trace) {
    namespace fs=std::filesystem;
    require_view(scene.extra_route() && scene.extra_route()->ticks()==0 && scene.main_resources_alive(),"Extra MAINE route not created at the real exit");
    const auto generation=scene.generation(),main_random=scene.process_random_state();
    const auto statistics=scene.main_state().run_statistics();
    const auto frame=scene.main_state().frames();const auto cursor=scene.main_state().random_cursor();
    const unsigned character=unsigned(scene.resident().playchar),shot_type=unsigned(scene.resident().shot_type);
    const auto endtype=scene.resident().end_type_ascii;
    trace<<"outgoing_extra "<<unsigned(endtype)<<' '<<statistics.std_frames<<' '<<statistics.items_spawned<<' '<<statistics.items_collected<<' '<<statistics.point_items_collected<<' '<<statistics.max_valued_point_items_collected<<' '<<statistics.enemies_gone<<' '<<statistics.enemies_killed<<' '<<statistics.slow_frames<<' '<<statistics.frames<<' '<<scene.main_state().score().score_delta;
    for(auto digit:statistics.score_digits)trace<<' '<<+digit;
    trace<<'\n';
    const auto capture=[&](const std::string& suffix) {
        const auto ticks=scene.extra_route() ? scene.extra_route()->ticks() : 0;
        const auto random=scene.process_random_state(),before=scene.generation();
        scene.repaint();const auto pixels=scene.frame().pixels;scene.repaint();
        require_view(scene.frame().pixels==pixels && scene.process_random_state()==random && scene.generation()==before &&
            (!scene.extra_route() || scene.extra_route()->ticks()==ticks),"Extra MAINE repaint consumed clock/RNG/process boundary");
        write_bmp((directory/(name+"-"+suffix+".bmp")).string(),scene.frame());
    };
    require_view(scene.resident().end_sequence==application::EndSequence::extra && scene.program()==application::Program::main,"end_extra did not publish ES_EXTRA before fade16");
    for(unsigned tick=1;tick<273;++tick) {
        scene.advance(0x2000|shot::input_shot,false,paint);
        require_view(scene.main_resources_alive() && scene.program()==application::Program::main && scene.generation()==generation &&
            scene.main_state().frames()==frame && scene.main_state().random_cursor()==cursor && scene.process_random_state()==main_random &&
            scene.extra_route()->main_tone()==100-int((tick-1)/16)*6,"Extra fade altered MAIN clock/RNG or resource lifetime");
        trace<<"mainfade "<<tick<<' '<<scene.extra_route()->main_tone()<<'\n';
        if(tick==128)capture("fade128");
    }
    scene.advance(shot::input_shot,false,paint);
    require_view(!scene.main_resources_alive() && !scene.dialog_active() && scene.program()==application::Program::maine && scene.generation()==generation+1 &&
        scene.process_random_state()==1 && scene.extra_route()->fade_ticks()==273 && scene.resident().end_type_ascii==endtype &&
        scene.resident().score_digits==statistics.score_digits && scene.resident().statistics.frames==statistics.frames,"Extra MAIN blackout did not publish and release into fresh MAINE");
    trace<<"mainfade 273 0\n";
    capture("black-main");
    for(unsigned tick=0;tick<99;++tick)scene.advance(shot::input_shot,false,paint);
    require_view(!scene.registration_scene() && scene.process_random_state()==1,"Extra MAINE shortened delay100");
    scene.advance(shot::input_shot,false,paint);
    require_view(scene.registration_scene() && scene.extra_route()->ticks()==373,"Extra registration did not begin at373");
    for(unsigned i=0;i<35;++i)scene.advance(shot::input_shot,false,paint);
    require_view(scene.registration_scene()->status()==registration::Status::editing && scene.registration_scene()->menu().place()!=score_file::no_entry,
        "Actual Extra score did not enter registration editing");
    capture("registration");
    const auto press=[&](std::uint16_t held) {scene.advance(0,false,paint);scene.advance(0,false,paint);scene.advance(held,false,paint);};
    for(unsigned i=0;i<(shot_type ? 8u : 1u);++i)press(shot::input_shot);
    if(shot_type) {
        require_view(scene.registration_scene()->menu().name_cursor()==7 && scene.registration_scene()->status()==registration::Status::editing,"Extra full name saved without explicit confirmation");
        press(shot::input_shot);
    } else press(0x2000);
    require_view(scene.registration_scene()->status()==registration::Status::fade_out && !scene.extra_route()->congratulations_scene(),"Extra congratulations preceded writer-close/registration blackout");
    const auto path=directory/name/"save"/"GENSOU.SCR";
    require_view(fs::is_regular_file(path) && fs::file_size(path)==1960,"Extra host writer did not close a complete score file");
    score_file::HostStore restarted(path.parent_path());
    for(unsigned section=0;section<10;++section) {
        score_file::Section decoded{};unsigned draws=0;
        require_view(!score_file::load_for(decoded,restarted.file(),std::uint8_t(section/5),std::uint8_t(section%5),[&]{++draws;return 0;}) && !draws,"Extra restart could not decode all ten saved sections");
        if(section==character*5+4) {
            require_view((decoded[score_file::cleared_offset]&(1u<<shot_type)) && decoded[score_file::stages_offset]==score_file::gaiji_all,"Extra clear flag/stage marker absent after restart");
            for(unsigned digit=0;digit<8;++digit)require_view(decoded[score_file::digits_offset+digit]==statistics.score_digits[digit]+score_file::gaiji_zero,"Extra saved score committed pending delta or changed digits");
        }
    }
    std::ifstream file(path,std::ios::binary);const Bytes saved{std::istreambuf_iterator<char>(file),{}};
    std::ofstream copy(directory/(name+"-GENSOU.SCR"),std::ios::binary);copy.write(reinterpret_cast<const char*>(saved.data()),saved.size());require_view(bool(copy),"Extra saved-file copy failed");
    const auto saved_random=scene.process_random_state();
    for(unsigned tick=0;tick<17;++tick) {scene.advance(0,false,paint);require_view(scene.registration_scene(),"Extra registration blackout returned early");}
    scene.advance(0,false,paint);
    require_view(scene.extra_route()->congratulations_scene() && !scene.extra_route()->verdict_scene() && !scene.registration_scene() &&
        scene.extra_route()->congratulations_scene()->picture_name()==maine::congratulations_picture(character,4) && scene.process_random_state()==saved_random,"Extra order/picture/RNG differs before congratulations");
    for(unsigned tick=0;tick<30;++tick)scene.advance(shot::input_shot,false,paint);
    require_view(scene.extra_route()->congratulations_scene()->animation().status()==maine::AnimationStatus::release,"Extra congratulation inherited confirmation");
    capture("congratulations");
    for(unsigned tick=0;tick<10;++tick)scene.advance(shot::input_shot,false,paint);
    require_view(scene.process_random_state()==saved_random && scene.extra_route()->congratulations_scene(),"Extra congratulation changed the registration LCG or skipped its wait");
    press(shot::input_shot);
    for(unsigned tick=0;tick<100 && scene.extra_route()->phase()==maine::ExtraPhase::congratulations;++tick)scene.advance(0,false,paint);
    require_view(scene.extra_route()->verdict_scene() && !scene.extra_route()->congratulations_scene() && scene.process_random_state()==saved_random,"Extra verdict preceded the congratulations blackout");
    for(unsigned tick=0;tick<1000 && scene.extra_route()->verdict_scene()->status()!=verdict::Status::release;++tick)scene.advance(shot::input_shot,false,paint);
    require_view(scene.extra_route()->verdict_scene()->status()==verdict::Status::release,"Extra verdict omitted its fresh press");capture("verdict");
    trace<<"verdict_rng "<<saved_random<<' '<<scene.process_random_state()<<' '<<scene.resident().statistics.std_frames<<'\n';
    press(shot::input_shot);
    for(unsigned tick=0;tick<100 && scene.extra_route();++tick)scene.advance(0,false,paint);
    require_view(scene.program()==application::Program::op && !scene.extra_route() && !scene.registration_scene() && !scene.main_resources_alive() &&
        scene.generation()==generation+2 && scene.process_random_state()==1,"Extra did not return to a fresh OP");
    const auto& flow=scene.last_extra_boundaries();require_view(flow.size()==10,"Extra MAINE child sequence incomplete");
    for(unsigned i=0;i<flow.size();++i) {require_view(unsigned(flow[i].kind)==i,"Extra MAINE child order differs");trace<<"extra_flow "<<i<<' '<<flow[i].tick<<'\n';}
    capture("fresh-op");
    scene.input(menu::Input::confirm);if(character)scene.input(menu::Input::right);scene.input(menu::Input::confirm);
    if(shot_type)scene.input(menu::Input::down);
    scene.input(menu::Input::confirm);
    require_view(scene.live_main() && scene.generation()==generation+3 && scene.resident().stage==0 && scene.resident().graze==0 &&
        !scene.main_state().boss_active() && !scene.main_state().clear_bonus() && !scene.main_state().extra_ending_requested(),"Second MAIN retained the preceding Extra run");
    require_view(scene.main_state().scoreboard().digits==std::array<std::uint8_t,8>{} && scene.main_state().score().score_delta==0,
        "Second MAIN inherited outgoing Extra score digits or pending delta");
    capture("second-main");
    trace<<"extra_maine "<<scene.generation()<<' '<<scene.process_random_state()<<' '<<flow[2].tick<<' '<<flow[4].tick<<' '<<flow[9].tick<<" fresh_op=1 second_main=1 muted=1\n";
}

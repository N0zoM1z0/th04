// Actual OP options/selection and authored STD combat/contact reach Quit.
// No forced hit, score, life, MAINE entry or verdict completion is injected.
void run_score_route_checks(const PiImage& background,const CdgSheet& numerals,
    const CdgSheet& labels,const CdgSheet& cursors,const PiImage& selection_background,
    const CdgSheet& portraits,const MainAssets& assets,const std::string& destination) {
    namespace fs=std::filesystem;
    const fs::path directory(destination);
    require_view(!fs::exists(directory) && assets.muted,"use fresh muted score-route controls");
    fs::create_directories(directory);
    const auto write=[&](const fs::path& path,const Bytes& bytes) {
        std::ofstream out(path,std::ios::binary);
        out.write(reinterpret_cast<const char*>(bytes.data()),bytes.size());
        require_view(bool(out),"score-route capture failed");
    };
    for(unsigned character=0;character<2;++character)for(unsigned rank=0;rank<4;++rank)
        for(unsigned profile=0;profile<5;++profile) {
        if(profile>=3 && rank!=1)continue;
        const auto name="c"+std::to_string(character)+"-r"+std::to_string(rank)+"-p"+std::to_string(profile);
        auto input=assets;const auto location=directory/name;fs::create_directories(location);
        input.save_directory=(location/"save").string();
        if(profile==4) {std::ofstream blocker(input.save_directory);blocker<<"blocked score directory";}
        Bytes standard{0,0,8};standard.insert(standard.end(),8,0);standard.push_back(9);
        standard.insert(standard.end(),8,16);standard.push_back(0);
        // Script0 has zero-score contact; script1 is shot down for50000.
        standard.push_back(2);
        for(unsigned script=0;script<2;++script) {
            const unsigned reward=script ? 50000 : 0;
            for(unsigned value:{9u,0x10u,128u,1u,0u,reward&255u,reward>>8,6u,100u,0u})
                standard.push_back(std::uint8_t(value));
        }
        standard.push_back(0);
        const auto wave=[&](unsigned frame,unsigned script,unsigned y) {
            for(unsigned value:{frame&255u,frame>>8,1u,script,0u,12u,(y*16)&255u,(y*16)>>8,255u,0u,0u})
                standard.push_back(std::uint8_t(value));
        };
        if(profile)wave(8,1,128);
        wave(64,0,320);wave(2000,0,304);
        standard.insert(standard.end(),2,0);const auto extent=standard.size()-2;
        standard[0]=std::uint8_t(extent);standard[1]=std::uint8_t(extent>>8);
        input.standard=standard;write(location/"finite.std",standard);
        FrontEnd scene(background,numerals,labels,cursors,selection_background,portraits,&input);
        std::ofstream sound_trace;
        if(assets.capture_sound_scenes) {
            sound_trace.open(location/"sound.txt",std::ios::binary);
            attach_sound_scene_trace(scene,sound_trace);
            if(profile!=4) {
                th04::portable::configuration::HostStore cfg(input.save_directory);
                cfg.complete_setup(2,2);cfg.save(cfg.options(),false);
                scene.enable_configuration();
            }
        }
        if(profile==4) {
            bool rejected=false;
            try {scene.enable_registration();}catch(const std::filesystem::filesystem_error&) {rejected=true;}
            catch(const std::runtime_error&) {rejected=true;}
            require_view(rejected && scene.program()==application::Program::op && !scene.live_main() && !scene.registration_scene(),
                "failed initial OP score recreation launched MAIN or MAINE");
            std::ofstream failure(location/"failure.txt",std::ios::binary);
            failure<<"FAILED op_recreate 0 fresh_op=0 muted=1\n";
            std::cout<<"SCORE_ROUTE_FAILED "<<name<<" op_recreate muted=1\n";continue;
        }
        scene.enable_registration();
        for(unsigned i=0;i<3;++i)scene.input(menu::Input::down);
        scene.input(menu::Input::confirm);
        if(!rank)scene.input(menu::Input::left);
        else for(unsigned i=1;i<rank;++i)scene.input(menu::Input::right);
        scene.input(menu::Input::down);scene.input(menu::Input::left);scene.input(menu::Input::left);
        scene.input(menu::Input::cancel);
        for(unsigned i=0;i<3;++i)scene.input(menu::Input::up);
        scene.input(menu::Input::confirm);if(character)scene.input(menu::Input::right);
        scene.input(menu::Input::confirm);scene.input(menu::Input::confirm);
        require_view(scene.live_main() && scene.resident().credit_lives==1 && scene.resident().config.rank==rank,
                     "score-route actual OP options/selection failed");
        const auto main_generation=scene.generation();
        for(unsigned frame=0;frame<1000 && !scene.main_state().game_over();++frame)
            scene.advance(profile && frame<50 ? shot::input_shot : 0,false,false);
        require_view(scene.main_state().game_over(),"finite STD contact did not reach Game Over");
        const auto statistics=scene.main_state().run_statistics();
        unsigned earned_score=0;
        for(unsigned i=8;i--;)earned_score=earned_score*10+statistics.score_digits[i];
        if(profile)require_view(earned_score>=50000 && scene.main_state().enemies().snapshot().killed_count>=2,
                               "actual shot kill did not earn registration score");
        unsigned clock=0;
        while(scene.live_main() && clock<650) {
            ++clock;std::uint16_t held=clock>=101 && clock<=109 ? shot::input_shot : 0;
            if(clock==114)held=0x2000; // Explicit Esc -> Quit after two released samples.
            scene.advance(held,false,false);
        }
        require_view(clock<650 && scene.score_route() && !scene.main_resources_alive() &&
            !scene.gameover_renderer() && scene.program()==application::Program::maine &&
            scene.generation()==main_generation+1 && scene.process_random_state()==1 &&
            scene.resident().statistics.std_frames==statistics.std_frames &&
            scene.resident().statistics.frames==statistics.frames && scene.resident().miss_count==1,
            "Quit did not publish the interrupted run and release MAIN into fresh MAINE");
        std::ofstream flow(location/"flow.txt",std::ios::binary);
        const auto capture=[&](const std::string& suffix) {
            const auto ticks=scene.score_route() ? scene.score_route()->ticks() : 0;
            const auto random=scene.process_random_state();
            scene.repaint();const auto once=scene.frame().pixels;scene.repaint();
            require_view(once==scene.frame().pixels && scene.process_random_state()==random &&
                (!scene.score_route() || scene.score_route()->ticks()==ticks),"score-route repaint advanced clock/RNG");
            write_bmp((location/(suffix+".bmp")).string(),scene.frame());
        };
        capture("delay");
        for(unsigned i=0;i<99;++i)scene.advance(shot::input_shot,false,false);
        require_view(!scene.registration_scene() && scene.process_random_state()==1,
                     "held confirmation shortened the score-route100-refresh delay");
        scene.advance(shot::input_shot,false,false);
        require_view(scene.registration_scene() && scene.registration_scene()->ticks()==0 &&
            scene.registration_scene()->menu().editable()==bool(profile),"natural score placement differs");
        const auto entered_place=scene.registration_scene()->menu().place();
        capture("registration-start");
        for(unsigned i=0;i<35;++i)scene.advance(shot::input_shot,false,false);
        capture("registration-edit");
        const auto press=[&](std::uint16_t held) {
            scene.advance(0,false,false);scene.advance(0,false,false);scene.advance(held,false,false);
        };
        if(profile==3) {
            const auto path=fs::path(input.save_directory)/"GENSOU.SCR";
            fs::rename(path,location/"committed-before");fs::create_directory(path);
            bool rejected=false;try {press(0x2000);}catch(const std::exception&) {rejected=true;}
            require_view(rejected && scene.score_route()->failed() && scene.registration_scene() &&
                !scene.score_route()->verdict_scene() && scene.program()==application::Program::maine &&
                scene.generation()==main_generation+1,"failed registration save continued into verdict/OP");
            const auto ticks=scene.score_route()->ticks(),seed=scene.process_random_state();
            scene.advance(shot::input_shot,false,false);
            require_view(scene.score_route()->ticks()==ticks && scene.process_random_state()==seed &&
                fs::is_regular_file(location/"committed-before") && fs::is_directory(path),
                "failed save retried or lost the previous committed file");
            std::ofstream failure(location/"failure.txt",std::ios::binary);
            failure<<"FAILED save "<<ticks<<" fresh_op=0 muted=1\n";
            std::cout<<"SCORE_ROUTE_FAILED "<<name<<" save muted=1\n";continue;
        }
        if(!profile)press(shot::input_shot);
        else {
            for(unsigned i=0;i<(profile==1 ? 1u : 8u);++i)press(shot::input_shot);
            if(profile==2) {
                require_view(scene.registration_scene()->menu().name_cursor()==7 &&
                    scene.registration_scene()->status()==registration::Status::editing,
                    "eight letters auto-saved before explicit Enter");
                capture("full-name");press(shot::input_shot);
            } else press(0x2000);
        }
        require_view(scene.registration_scene()->status()==registration::Status::fade_out &&
            scene.program()==application::Program::maine,"save did not precede registration blackout");
        const auto file=fs::path(input.save_directory)/"GENSOU.SCR";
        require_view(fs::is_regular_file(file) && fs::file_size(file)==1960,"registration failed real writer close");
        for(unsigned i=0;i<17;++i) {
            scene.advance(0,false,false);require_view(!scene.score_route()->verdict_scene(),
                "verdict began before registration finished its blackout");
        }
        scene.advance(0,false,false);
        require_view(scene.score_route()->verdict_scene() && !scene.registration_scene() &&
            scene.generation()==main_generation+1,"registration returned to OP before verdict");
        unsigned verdict_wait=0;
        while(scene.score_route()->verdict_scene()->status()!=verdict::Status::release && verdict_wait<1000) {
            scene.advance(shot::input_shot,false,false);++verdict_wait;
        }
        require_view(verdict_wait<1000,"score-route verdict did not reach release/press");
        capture("verdict");
        for(unsigned i=0;i<8;++i)scene.advance(shot::input_shot,false,false);
        require_view(scene.program()==application::Program::maine,"inherited key escaped score-route verdict");
        press(shot::input_shot);
        for(unsigned i=0;i<35 && scene.program()==application::Program::maine;++i)scene.advance(0,false,false);
        require_view(scene.program()==application::Program::op && !scene.score_route() &&
            scene.generation()==main_generation+2 && scene.process_random_state()==1 &&
            !scene.main_resources_alive(),"verdict did not release score route and enter fresh OP");
        capture("fresh-op");
        for(const auto& boundary:scene.last_score_boundaries())flow<<int(boundary.kind)<<' '<<boundary.tick<<'\n';
        flow.flush();require_view(bool(flow),"score route boundary journal failed");
        score_file::HostStore reopened(input.save_directory);score_file::Section section{};
        th04::portable::rng::Lcg32 random;
        require_view(!score_file::load_for(section,reopened.file(),std::uint8_t(character),std::uint8_t(rank),
            [&]{return random.next15();}),"score-only saved file failed independent reopen");
        if(profile)for(unsigned i=0;i<(profile==1 ? 1u : 8u);++i)
            require_view(section[score_file::names_offset+entered_place*score_file::name_stride+i]==0xaa,
                "saved natural name differs");
        // Both ordinary menu/selection and refreshed MAIN resources remain usable.
        scene.input(menu::Input::confirm);scene.input(menu::Input::confirm);scene.input(menu::Input::confirm);
        require_view(scene.live_main() && scene.main_resources_alive() &&
            scene.generation()==main_generation+3 && scene.main_state().frames()==0 &&
            scene.resident().miss_count==0,"fresh OP failed second MAIN initialization");
        std::cout<<"SCORE_ROUTE "<<name<<" score_digits=";
        for(auto digit:statistics.score_digits)std::cout<<+digit;
        std::cout<<" std="<<statistics.std_frames<<" frames="<<statistics.frames
                 <<" gameover_ticks="<<clock<<" fresh_op=1 second_main=1 muted=1\n";
    }
}

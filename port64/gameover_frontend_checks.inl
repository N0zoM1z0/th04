// Bounded frontend replay body: authored finite STD contact, real lifecycle,
// held keyboard sampling, frozen display/TRAM and actual Continue host store.
void run_gameover_checks(const PiImage& background,const CdgSheet& numerals,
    const CdgSheet& labels,const CdgSheet& cursors,const PiImage& selection_background,
    const CdgSheet& portraits,const MainAssets& assets,const std::string& destination) {
    namespace fs=std::filesystem;
    const fs::path directory(destination);
    require_view(!fs::exists(directory),"use a fresh Game Over fixture directory");
    fs::create_directories(directory);
    require_view(assets.muted,"Game Over fixtures must be muted");
    // A replay protocol uses LF on both hosts, independent of CRT text mode.
    std::ofstream log(directory/"trace.txt",std::ios::binary),snapshots(directory/"snapshots.txt",std::ios::binary);
    require_view(bool(log) && bool(snapshots),"Game Over journal cannot open");
    struct Restore {std::streambuf* previous;~Restore(){std::cout.rdbuf(previous);}} restore{std::cout.rdbuf(log.rdbuf())};
    std::ostream binary(restore.previous);
#ifdef _WIN32
    _setmode(_fileno(stdout),_O_BINARY);
#endif
    const auto write=[&](const fs::path& path,const Bytes& bytes) {
        std::ofstream f(path,std::ios::binary);require_view(bool(f),"Game Over capture cannot open");
        f.write(reinterpret_cast<const char*>(bytes.data()),bytes.size());require_view(bool(f),"Game Over capture write failed");
    };
    // Valid MAP metadata plus genuine ACTIVATE128/hp1/score0, WAIT100, KILL.
    // Later waves keep the stage VM live and test three real Continue credits.
    Bytes standard{0,0,8};standard.insert(standard.end(),8,0);standard.push_back(9);
    standard.insert(standard.end(),8,16);standard.push_back(0);
    for(auto byte:{1,9,0x10,128,1,0,0,0,6,100,0,0})standard.push_back(std::uint8_t(byte));
    for(unsigned frame:{64u,300u,500u,700u,2000u}) {
        standard.push_back(std::uint8_t(frame));standard.push_back(std::uint8_t(frame>>8));
        standard.push_back(1);standard.push_back(0);
        standard.push_back(0);standard.push_back(12);
        const unsigned y=(frame==64 ? 320 : 304)*16;
        standard.push_back(std::uint8_t(y));standard.push_back(std::uint8_t(y>>8));
        standard.push_back(255);standard.push_back(0);standard.push_back(0);
    }
    standard.insert(standard.end(),2,0);const unsigned extent=unsigned(standard.size()-2);
    standard[0]=std::uint8_t(extent);standard[1]=std::uint8_t(extent>>8);write(directory/"finite.std",standard);
    for(unsigned character=0;character<2;++character)for(unsigned profile=0;profile<5;++profile)
        for(unsigned paint=0;paint<(profile<2 ? 2u : 1u);++paint) {
        const auto name="c"+std::to_string(character)+"-p"+std::to_string(profile)+"-paint"+std::to_string(paint);
        auto input=assets;input.standard=standard;input.save_directory=(directory/name/"save").string();
        fs::create_directories(directory/name);
        if(profile==4) {std::ofstream blocker(input.save_directory);blocker<<"blocked score directory";}
        FrontEnd scene(background,numerals,labels,cursors,selection_background,portraits,&input);
        scene.enable_registration();
        // Actual OP option and character-selection paths, with one life.
        for(unsigned i=0;i<3;++i)scene.input(menu::Input::down);
        scene.input(menu::Input::confirm);scene.input(menu::Input::down);
        scene.input(menu::Input::left);scene.input(menu::Input::left);scene.input(menu::Input::cancel);
        for(unsigned i=0;i<3;++i)scene.input(menu::Input::up);
        scene.input(menu::Input::confirm);if(character)scene.input(menu::Input::right);
        scene.input(menu::Input::confirm);scene.input(menu::Input::confirm);
        require_view(scene.live_main() && scene.resident().credit_lives==1,"fixture OP handoff/options failed");
        const unsigned runs=profile==3 ? 4 : 1;
        for(unsigned run=0;run<runs;++run) {
            const auto stem=name+"-g"+std::to_string(run);const auto location=directory/stem;
            fs::create_directories(location);
            std::ofstream events(location/"events.txt",std::ios::binary),keys(location/"keys.txt",std::ios::binary),initial(location/"initial.txt",std::ios::binary);
            unsigned clock=0;int tone=100;bool began=false,failed=false,terminal_captured=false;
            std::function<void()> capture_terminal;
            Bytes last_state;
            scene.set_gameover_observer([&](const gameover::Event& event) {
                const auto& main=scene.main_state();const auto& resources=main.score();const auto& board=main.scoreboard();
                if(!began) {
                    began=true;const auto& resident=scene.resident();
                    initial<<unsigned(resident.resource_stage)<<' '<<unsigned(resident.credit_lives)<<' '
                        <<unsigned(resident.credit_bombs)<<" 0 "<<+resources.power<<' '<<resources.power_overflow<<' '
                        <<+resources.dream_items_collected<<' '<<resources.dream_score<<' '<<+resources.remaining_lives<<' '
                        <<+resources.remaining_bombs<<' '<<board.delta<<' '<<board.frame_delta<<' '<<+board.unused<<' '
                        <<+board.extends<<' '<<+board.hiscore_popup_shown;
                    for(const auto* values:{&board.digits,&board.hiscore,&board.temporary,&board.hud})for(auto value:*values)initial<<' '<<+value;
                    initial<<'\n';
                    const auto* renderer=scene.gameover_renderer();require_view(renderer,"Game Over has no frozen graphics owner");
                    write(location/"initial.indices",renderer->indexed());write(location/"initial.tram",renderer->text().bytes());
                    write(location/"initial.pal",Bytes(renderer->palette().begin(),renderer->palette().end()));
                }
                events<<clock<<' '<<int(event.kind)<<' '<<event.left<<' '<<event.row<<' '<<event.value<<' '<<event.attribute<<' ';
                if(event.text.empty())events<<'-';
                else for(auto byte:event.text)events<<std::hex<<std::setw(2)<<std::setfill('0')<<unsigned(std::uint8_t(byte))<<std::dec;
                events<<'\n';
                if(event.kind==gameover::Kind::tone)tone=event.value;
                last_state={resources.power,resources.dream_items_collected,resources.remaining_lives,
                            resources.remaining_bombs,board.digits[0]};
                // Retain the final Continue display at its real request boundary,
                // before MAIN resumes its interrupted frame and releases the scene.
                if(event.kind==gameover::Kind::wipe && clock>114 && capture_terminal &&
                   main.game_over()->phase()==gameover::Phase::final_in && !terminal_captured) {
                    terminal_captured=true;capture_terminal();
                }
            });
            for(unsigned i=0;i<1000 && !scene.main_state().game_over();++i)scene.advance(0,false,paint!=0);
            auto& main=scene.main_state();
            require_view(main.game_over() && main.life().misses==run+1 && main.enemies().snapshot().killed_count==run+1,
                         "real finite STD contact did not enter Game Over");
            if(!run)require_view(main.frames()==104 && main.run_statistics().std_frames==105,"first contact/Game Over prefix clock differs");
            const auto frozen_frame=main.frames();const auto frozen_std=main.run_statistics().std_frames;
            const auto frozen_ring=main.random_cursor();const auto frozen_position=main.player().position().current;
            const auto frozen_indices=scene.gameover_renderer()->indexed();
            const auto snapshot=[&] {
                scene.repaint();const auto once=scene.frame().pixels;scene.repaint();
                require_view(scene.frame().pixels==once && scene.frame().indices==frozen_indices,"Game Over repaint changed frozen display");
                const auto tram=scene.gameover_renderer()->text().bytes();Bytes rgb(640*400*3);
                for(unsigned i=0;i<once.size();++i) {rgb[i*3]=std::uint8_t(once[i]>>16);rgb[i*3+1]=std::uint8_t(once[i]>>8);rgb[i*3+2]=std::uint8_t(once[i]);}
                snapshots<<stem<<' '<<clock<<' '<<tone<<'\n';
                for(const Bytes* data:{&frozen_indices,&tram,static_cast<const Bytes*>(&rgb)})binary.write(reinterpret_cast<const char*>(data->data()),data->size());
                require_view(bool(binary),"Game Over binary capture failed");
            };
            capture_terminal=snapshot;
            snapshot();
            while(main.game_over() && !main.game_over()->finished() && clock<650) {
                ++clock;std::uint16_t held=0;
                if(clock>=101 && clock<=109)held=shot::input_shot;
                // Release acknowledgement at110/111, then release Down at
                // 113/114. Both samples must clear before a new confirmation.
                if(profile==2 && clock==112)held=player::down;
                if(clock==(profile==2 ? 115u : 114u))held=profile==1 ? 0x2000 : shot::input_shot;
                keys<<player::input_from_host_actions(held)<<'\n';
                if(clock==100 || clock==111) {
                    const auto ticks=main.game_over()->ticks();
                    require_view(!scene.input(menu::Input::cancel) && main.game_over()->ticks()==ticks,
                                 "Esc discrete input closed or advanced Game Over");
                }
                try {scene.advance(held,false,paint!=0);}
                catch(const std::exception&) {
                    if(profile!=4)throw;
                    require_view(clock==114 && main.frames()==frozen_frame && main.scoreboard().digits[0]==0 &&
                                 main.score().remaining_lives==1 && main.game_over()->phase()==gameover::Phase::menu,
                                 "failed real writer reset or advanced the paused run");failed=true;break;
                }
                if(main.game_over()) {
                    if(profile==2 && clock==112)require_view(main.game_over()->selected()==1,
                        "Down did not select Quit after released acknowledgement");
                    require_view(main.frames()==frozen_frame && main.run_statistics().std_frames==frozen_std &&
                        main.random_cursor()==frozen_ring && main.player().position().current.x==frozen_position.x &&
                        main.player().position().current.y==frozen_position.y && !scene.dialog_active() && scene.slowdown()==1,
                        "Game Over advanced MAIN/STD/RNG/player or inherited gameplay slowdown");
                    require_view(scene.gameover_renderer()->indexed()==frozen_indices,"frozen graphics mutated");
                    if(clock%16==0 || clock==95 || clock==100 || clock==114 || main.game_over()->finished())snapshot();
                }
                if(clock==109 && !(profile==3 && run==3))require_view(main.game_over()->phase()==gameover::Phase::menu &&
                    main.scoreboard().digits[0]==run,"held acknowledgement confirmed or repeated a menu action");
            }
            require_view(clock<650,"Game Over fixture did not finish");
            events.flush();keys.flush();initial.flush();
            std::ofstream end(location/"end.txt",std::ios::binary);
            if(failed) {
                end<<"FAILED "<<clock<<'\n';
                require_view(fs::is_regular_file(input.save_directory),"failed writer replaced the blocker");
            } else {
                const bool quit=bool(main.game_over());
                if(profile==1 || profile==2 || (profile==3 && run==3))
                    require_view(quit,"expected Quit path unexpectedly accepted Continue");
                end<<"END "<<(quit ? 1 : 0)<<' '<<clock<<' '<<tone;
                for(auto value:last_state)end<<' '<<+value;
                end<<'\n';
                if(quit) {
                    require_view(main.score_registration_requested() && scene.program()==application::Program::main &&
                        scene.resident().end_sequence==application::EndSequence::score,"Quit omitted score-only MAINE request");
                    const auto ticks=main.game_over()->ticks();for(unsigned i=0;i<3;++i)scene.advance(0,false,paint!=0);
                    require_view(main.frames()==frozen_frame && main.game_over()->ticks()==ticks && tone==0,
                                 "pending MAINE route replayed Game Over or its frame tail");
                } else {
                    require_view(main.frames()==frozen_frame+1 && main.run_statistics().std_frames==frozen_std &&
                        main.scoreboard().digits[0]==run+1 && !scene.gameover_renderer(),"Continue repeated the STD prefix or retained Game Over graphics");
                    const auto path=fs::path(input.save_directory)/"GENSOU.SCR";
                    require_view(fs::is_regular_file(path) && fs::file_size(path)==score_file::section_size*score_file::section_count,"Continue did not finish real host saving");
                    score_file::HostStore reopened(input.save_directory);score_file::Section section{};
                    th04::portable::rng::Lcg32 random;
                    require_view(!score_file::load_for(section,reopened.file(),std::uint8_t(character),1,
                        [&]{return random.next15();}),"Continue file failed independent reopen");
                    scene.advance(0,false,paint!=0);require_view(main.run_statistics().std_frames==frozen_std+1,"next STD prefix missing");
                }
            }
            log<<"GAMEOVER fixture="<<stem<<" frame="<<frozen_frame<<" std="<<frozen_std
               <<" ticks="<<clock<<" result="<<(failed ? "failed_writer" : main.game_over() ? "score_maine_pending" : "continue")
               <<" credits="<<+main.scoreboard().digits[0]<<" frozen=1 muted=1\n";
            scene.set_gameover_observer({});
        }
    }
}

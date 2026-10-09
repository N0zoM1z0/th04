// Actual idle OP -> four original recorded demos -> fresh OP; no actor controls.
void run_demo_checks(const PiImage& background,const CdgSheet& numerals,
    const CdgSheet& labels,const CdgSheet& cursors,const PiImage& selection_background,
    const CdgSheet& portraits,const MainAssets& assets,const std::string& destination) {
    namespace fs=std::filesystem;const fs::path out(destination),inputs(assets.save_directory);
    require_view(assets.muted && !fs::exists(out),"demo checks require fresh muted outputs");fs::create_directories(out);
    for(unsigned rank:{0u,3u})for(unsigned abort:{0u,1u}) {
        const auto dir=out/("rank"+std::to_string(rank)+"-abort"+std::to_string(abort));fs::create_directories(dir/"save");
        fs::copy_file(inputs/"scores.SCR",dir/"save"/"GENSOU.SCR");auto input=assets;input.save_directory=(dir/"save").string();
        FrontEnd scene(background,numerals,labels,cursors,selection_background,portraits,&input);scene.enable_registration();
        while(scene.menu_state().selection()!=unsigned(menu::MainChoice::options))scene.input(menu::Input::down);
        scene.input(menu::Input::confirm);while(scene.menu_state().options().rank!=rank)scene.input(menu::Input::right);
        if(rank==3) {
            while(scene.menu_state().selection()!=unsigned(menu::OptionChoice::turbo))scene.input(menu::Input::down);
            if(scene.menu_state().options().turbo)scene.input(menu::Input::right);
        }
        // Options idle accumulates beyond640 without a demo. The Cancel sample
        // still belongs to that option frame and resets the counter on return.
        for(unsigned i=0;i<650;++i)scene.advance(0,false,false);
        require_view(!scene.demo_active() && scene.demo_idle_frames()==650,"options idle replay gate");
        scene.input(menu::Input::cancel);scene.advance(0x2000,false,false);
        require_view(scene.demo_idle_frames()==0 && !scene.demo_active(),"option return idle ordering");
        const auto baseline=score_file::HostStore(dir/"save").file().bytes();
        std::ofstream trace(dir/"events.txt",std::ios::binary);
        for(unsigned number=1;number<=4;++number) {
            const auto generation=scene.generation();const auto resident_seed=scene.resident().random_seed_source;
            for(unsigned i=0;i<640;++i){scene.advance(0,false,false);require_view(!scene.demo_active(),"demo started before640 previous idle frames");}
            require_view(scene.resident().random_seed_source==resident_seed+640,"menu seed accumulation");
            scene.advance(0,false,true);require_view(scene.demo_active() && scene.program()==application::Program::op,"idle demo preparation replaced OP early");
            for(unsigned i=0;i<18;++i)scene.advance(0,false,true);
            require_view(scene.live_main() && scene.generation()==generation+1 && scene.resident().demo_number==number,"demo MAIN process entry");
            const unsigned stages[]{3,0,2,1},characters[]{0,1,0,1},shots[]{0,0,1,1};
            auto& main=scene.main_state();require_view(scene.resource_stage()==stages[number-1] && scene.resident().stage==stages[number-1] &&
                unsigned(scene.resident().playchar)==characters[number-1] && unsigned(scene.resident().shot_type)==shots[number-1] &&
                main.rank()==2 && main.turbo() && main.score().power==128 && main.scoreboard().performance==20 &&
                scene.resident().config.turbo==(rank==0),"demo resident/local setup");
            trace<<"START "<<number<<' '<<scene.resource_stage()<<' '<<scene.process_random_state()<<' '<<scene.resident().random_seed_source<<'\n';
            write_bmp((dir/("demo"+std::to_string(number)+"-start.bmp")).string(),scene.frame());
            unsigned refreshes=0;const unsigned abort_keys[]{1,0x20,0x2000,0x4000};
            while(scene.program()==application::Program::main && refreshes<7000) {
                const auto frame=scene.main_state().frames();
                const auto physical=abort && frame==120 ? abort_keys[number-1] : 0;
                scene.advance(std::uint16_t(physical),false,false);++refreshes;
                if(scene.program()!=application::Program::main)break;
                const auto& m=scene.main_state();const auto sample=m.demo_sample();
                if(m.frames()!=frame || m.demo_exit_requested()) {
                    const auto& p=m.player().position();
                    trace<<"FRAME "<<number<<' '<<frame<<' '<<sample.input<<' '<<+sample.shift<<' '<<sample.replaced<<' '<<sample.finished
                         <<' '<<p.current.x<<' '<<p.current.y<<' '<<+m.life().miss_time<<' '<<+m.score().remaining_lives<<' '
                         <<+m.score().remaining_bombs<<' '<<m.random_cursor()<<' '<<scene.process_random_state()<<'\n';
                }
                if(m.frames()!=frame && (m.frames()==64 || m.frames()==1000 || m.frames()==3000)) {
                    scene.repaint();const auto pixels=scene.frame().pixels;const auto rng=scene.process_random_state();scene.repaint();
                    require_view(scene.frame().pixels==pixels && scene.process_random_state()==rng && m.frames()==frame+1,"demo repaint advanced state");
                    write_bmp((dir/("demo"+std::to_string(number)+"-frame"+std::to_string(m.frames())+".bmp")).string(),scene.frame());
                }
                require_view(!m.game_over(),"recorded demo entered blocking Game Over before callback exit");
            }
            require_view(scene.program()==application::Program::op && scene.generation()==generation+2 && refreshes<7000 &&
                scene.menu_state().selection()==0 && scene.menu_state().options().rank==rank && !scene.main_resources_alive(),"demo fresh OP return");
            require_view(scene.resident().statistics.frames==(abort ? 120 : 3996),"demo frame3996/physical-abort boundary");
            require_view(scene.resident().random_seed_source==resident_seed+640,"demo or fades advanced resident seed");
            require_view(score_file::HostStore(dir/"save").file().bytes()==baseline,"demo changed valid physical scores");
            scene.repaint();write_bmp((dir/("demo"+std::to_string(number)+"-returned.bmp")).string(),scene.frame());
            trace<<"RETURN "<<number<<' '<<refreshes<<' '<<scene.generation()<<' '<<scene.resident().statistics.frames<<' '<<scene.process_random_state()<<'\n';
        }
        scene.input(menu::Input::confirm);scene.input(menu::Input::confirm);scene.input(menu::Input::confirm);
        require_view(scene.live_main() && scene.resident().demo_number==0 && scene.main_state().rank()==rank &&
            scene.main_state().turbo()==(rank==0),"ordinary MAIN after demo cycle");
        std::cout<<"DEMO rank="<<rank<<" abort="<<abort<<" visits=4 fresh_op=1 ordinary_main=1 muted=1\n";
    }
}

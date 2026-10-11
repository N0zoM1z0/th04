// Actual ordinary FrontEnd OP/demo route. Ten complete displays per demo,
// plus every before-update/terminal selected-state boundary. No host window.
void run_demo_picture_checks(const PiImage& background,const CdgSheet& numerals,
    const CdgSheet& labels,const CdgSheet& cursors,const PiImage& selection_background,
    const CdgSheet& portraits,const MainAssets& assets,const std::string& destination) {
    namespace fs=std::filesystem;const fs::path out(destination),inputs(assets.save_directory);
    require_view(assets.muted && !fs::exists(out),"picture capture requires fresh muted output");
    fs::create_directories(out/"save");
    fs::copy_file(inputs/"GENSOU.SCR",out/"save/GENSOU.SCR");
    fs::copy_file(inputs/"MIKO.CFG",out/"save/MIKO.CFG");
    auto input=assets;input.save_directory=(out/"save").string();
    FrontEnd scene(background,numerals,labels,cursors,selection_background,portraits,&input);
    scene.enable_registration();
    const std::array<unsigned,10> samples{1,2,3,72,73,74,1952,3379,3709,3996};
    std::ofstream trace(out/"state.txt"),displays(out/"displays.txt"),shakes(out/"shake.txt");
    require_view(bool(trace) && bool(displays) && bool(shakes),"cannot open demo picture trace");
    const auto hexadecimal=[&](const auto& bytes) {
        constexpr char digits[]="0123456789abcdef";
        for(auto byte:bytes)trace<<digits[unsigned(byte)>>4]<<digits[unsigned(byte)&15];
    };
    for(unsigned number=1;number<=4;++number) {
        unsigned waits=0;
        while(!scene.live_main() && waits++<1000)scene.advance(0,false,false);
        require_view(scene.live_main() && scene.resident().demo_number==number && scene.main_state().frames()==0,"demo entry order");
        const auto base_draws=scene.process_random_draws(),base_samples=scene.main_state().random_samples();
        demo::Replay replay(input.replays[number-1]);
        for(unsigned frame=0;frame<=3996;++frame) {
            const auto& m=scene.main_state();const auto& r=scene.resident();const auto sample=replay.sample(std::uint16_t(frame),0,0);
            require_view(m.frames()==frame,"demo frame extent");const auto& life=m.life();const auto& player=m.player().position().current;
            trace<<number<<' '<<frame<<' '<<(sample.finished?'T':'I')<<' '<<sample.input<<' '<<+sample.shift<<' '<<+r.stage<<' ';
            hexadecimal(m.scoreboard().digits);trace<<' '<<m.score().score_delta<<' '<<m.scoreboard().frame_delta<<' '<<scene.process_random_state()<<' ';
            hexadecimal(m.random_ring_bytes());trace<<' '<<m.random_cursor()<<' '<<player.x<<' '<<player.y<<' '<<+m.score().power<<' '
                <<+life.hit<<' '<<+life.invincibility<<' '<<+life.respawn_time<<' '<<+m.score().remaining_lives<<' '<<+m.score().remaining_bombs<<' '
                <<+r.miss_count<<' '<<+r.bombs_used<<' '<<scene.process_random_draws()-base_draws<<' '<<m.random_samples()-base_samples<<'\n';
            scene.advance(0,false,false);
            if(frame<3996) {
                const auto& s=scene.main_state().playfield_shake();const auto shift=scene.main_state().playfield_shift();
                shakes<<number<<' '<<frame+1<<' '<<s.x<<' '<<s.y<<' '<<s.time<<' '<<int(s.redraw)<<' '
                    <<shift.x<<' '<<shift.y<<' '<<shift.invalidate<<'\n';
            }
            require_view(scene.main_state().demo_sample().input==sample.input && scene.main_state().demo_sample().shift==sample.shift,"demo consumed sample");
            if(frame<3996 && std::find(samples.begin(),samples.end(),frame+1)!=samples.end()) {
                scene.repaint();const auto& display=scene.frame();
                require_view(display.width==640 && display.height==400 && display.indices.size()==256000,"complete native display extent");
                const auto stem="demo"+std::to_string(number)+"-frame"+std::to_string(frame+1);
                std::ofstream indices(out/(stem+".indices"),std::ios::binary),rgb(out/(stem+".rgb"),std::ios::binary),tram(out/(stem+".tram"),std::ios::binary);
                indices.write(reinterpret_cast<const char*>(display.indices.data()),display.indices.size());
                for(auto color:display.pixels) {rgb.put(char(color>>16));rgb.put(char(color>>8));rgb.put(char(color));}
                const auto text=main_text_plane(scene.main_state(),scene.resident().demo_number).bytes();
                require_view(text.size()==8000,"complete native TRAM extent");tram.write(reinterpret_cast<const char*>(text.data()),text.size());
                require_view(bool(indices) && bool(rgb) && bool(tram),"complete native display write");
                displays<<number<<' '<<frame+1<<' '<<scene.resource_stage()<<' '<<stem<<' '
                    <<scene.main_state().life().palette_tone<<' '<<scene.renderer_display_line()<<'\n';
            }
        }
        waits=0;while(scene.program()==application::Program::main && waits++<200)scene.advance(0,false,false);
        require_view(scene.program()==application::Program::op,"natural demo exit");
    }
    require_view(score_file::HostStore(out/"save").file().bytes()==score_file::HostStore(inputs).file().bytes(),"demo physical score drift");
    require_view(bool(trace) && bool(displays) && bool(shakes),"demo picture trace write failure");
}

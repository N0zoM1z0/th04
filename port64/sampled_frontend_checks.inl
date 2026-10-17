// Headless controls execute the same sampled frontend entry as both windows.
void run_sampled_frontend_checks(const PiImage& background,const CdgSheet& numerals,const CdgSheet& labels,
    const CdgSheet& cursors,const PiImage& selection_background,const CdgSheet& portraits,const MainAssets& original) {
    namespace fs=std::filesystem;const fs::path directory(original.sampled_input_checks);
    require_view(original.muted && !fs::exists(directory),"sampled frontend checks need fresh muted outputs");fs::create_directories(directory);
    MainAssets assets=original;assets.save_directory=(directory/"save").string();fs::create_directories(assets.save_directory);
    const auto exercise=[&](bool observed) {
    host_window::Trace trace(observed ? (directory/"trace").string() : "",true);
    FrontEnd scene(background,numerals,labels,cursors,selection_background,portraits,&assets);
    scene.enable_registration();scene.input(menu::Input::confirm);scene.input(menu::Input::confirm);scene.input(menu::Input::confirm);
    require_view(scene.live_main(),"sampled frontend did not enter MAIN");
    std::ofstream log(directory/(observed ? "polls.txt" : "unobserved-polls.txt"));
    std::vector<std::uint32_t> frames;unsigned calls=0,observations=0;std::uint64_t sequence=0;std::int64_t poll_begin=0;
    pc98_input::Snapshot previous;
    const pc98_input::Observer observer=[&](const pc98_input::Observation& sample) {
        require_view(sample.before.actions==previous.actions && sample.before.shift==previous.shift,"observer lost actual latch continuity");
        if(observations==0)require_view(sample.after.actions==0x200 && sample.physical.keys[8]==0x10,"observer initial keypad sample");
        if(observations==1)require_view(sample.physical.keys==pc98_input::BiosKeys{} && sample.after.actions==0x200,"observer must record retained high action after physical release");
        if(observations==2)require_view(sample.before.actions==0x200 && sample.after.actions==4 && !sample.after.shift,"observer tail reset must record both latch values");
        previous=sample.after;++observations;
        trace.input_poll(sequence,poll_begin,host_window::now_ns(),sample,true,scene.window_snapshot());
    };
    const auto advance=[&](const pc98_input::SampleSource& source) {
        ++sequence;const auto begin=host_window::now_ns();const auto slowdown=scene.slowdown();
        const pc98_input::SampleSource watched=[&](pc98_input::Operation op){poll_begin=host_window::now_ns();return source(op);};
        scene.advance_sampled(0,false,watched,false,observed ? observer : pc98_input::Observer{});
        if(observed)trace.refresh(sequence,begin,host_window::now_ns(),begin,{},true,slowdown,scene.slowdown(),scene.window_snapshot());
    };
    pc98_input::Sample diagonal;diagonal.keys[8]=0x10;diagonal.shift=true;
    pc98_input::Sample shifted_none;shifted_none.shift=true;pc98_input::Sample left;left.keys[7]=8;
    const std::array<pc98_input::Sample,3> initial{{diagonal,shifted_none,left}};
    const pc98_input::SampleSource first=[&](pc98_input::Operation op){
        require_view(calls<3 && op==(calls==1 ? pc98_input::Operation::sense : pc98_input::Operation::reset),"initial sampled frontend poll order");
        frames.push_back(scene.main_state().frames());log<<calls<<' '<<int(op)<<' '<<scene.main_state().frames()<<'\n';return initial[calls++];
    };
    advance(first);
    require_view(frames==std::vector<std::uint32_t>({0,0,0}) && scene.main_state().frames()==1,"tail sample must precede frame counter increment");
    require_view(scene.main_state().player_input()==0x200 && scene.main_state().consumed_input()==4 && scene.sampled_input().actions==4,"frontend uses sampled player and tail words separately");
    const auto first_position=scene.main_state().player().position().current;
    require_view(first_position.x==192*16+24 && first_position.y==320*16-24,"sampled frontend keypad/Shift movement");
    pc98_input::Sample physical;
    const pc98_input::SampleSource source=[&](pc98_input::Operation op){log<<calls++<<' '<<int(op)<<' '<<scene.main_state().frames()<<'\n';return physical;};
    advance(source);
    require_view(scene.main_state().player_input()==4 && !scene.main_state().consumed_input(),"head OR preserves the previous actual tail sample");
    require_view(scene.main_state().player().position().current.x==first_position.x-64,"tail/head retention must reach the real frontend player");
    const auto before=scene.main_state().frames(),random=scene.process_random_state();const auto ring=scene.main_state().random_ring_bytes();
    physical.keys[0]=1;advance(source);
    require_view(scene.pause_active() && scene.main_state().frames()==before,"sampled Cancel must own pause entry without a host cancel argument");
    physical={};for(unsigned i=0;i<8;++i)advance(source);
    require_view(scene.pause_active() && scene.main_state().frames()==before && scene.process_random_state()==random && scene.main_state().random_ring_bytes()==ring,"sampled pause changed actors or RNG");
    physical.keys[5]=2;for(unsigned i=0;i<4;++i)advance(source);
    require_view(scene.pause_active(),"sampled pause skipped final release");physical={};
    for(unsigned i=0;i<4 && scene.pause_active();++i)advance(source);
    require_view(!scene.pause_active() && scene.main_state().frames()==before+1,"sampled pause must resume its original frame once");
    require_view(!scene.main_state().player_input() && !scene.sampled_input().actions,"sampled pause result must reach MAIN and its tail");
    require_view(!observed || observations==calls,"observer omitted a real frontend sample");
    trace.finish(scene.window_snapshot());
    std::ostringstream wire;th04::portable::demo_wire::pools(wire,0,scene.main_state(),stage::Program(assets.standard));
    wire<<scene.process_random_state()<<' '<<scene.process_random_draws()<<' '<<scene.main_state().frames()<<' '
        <<scene.main_state().player_input()<<' '<<scene.main_state().consumed_input()<<'\n';
    for(const auto byte:scene.main_state().random_ring_bytes())wire.put(char(byte));
    return std::make_pair(wire.str(),calls);
    };
    const auto baseline=exercise(false),observed=exercise(true);
    require_view(baseline==observed,"read-only input observer changed complete pools,frame, input or RNG");
    std::ofstream result(directory/"result.txt");result<<"sampled_frontend=pass polls="<<observed.second<<" frames=3 observer_equal=1\n";
}

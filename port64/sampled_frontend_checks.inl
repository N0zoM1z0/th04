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

    // Exercise the actual window byte-source entry with a persistent keyboard,
    // explicit elapsed input and portable CPU availability. No expected action
    // word is supplied to the device or the game. The repeat make arrives after
    // the tail's Shot read, so using a final matrix would change this result.
    FrontEnd elapsed(background,numerals,labels,cursors,selection_background,portraits,&assets);
    host_window::Keyboard keyboard(0,host_window::Keyboard::available_cpu);
    keyboard.key(host_window::HostKey::shot,true,0);
    elapsed.enable_registration();elapsed.input(menu::Input::confirm);
    elapsed.input(menu::Input::confirm);elapsed.input(menu::Input::confirm);
    require_view(elapsed.live_main(),"elapsed keyboard frontend did not enter MAIN");
    unsigned polls=0,reads=0,total_reads=0;std::int64_t time=0;bool stagger=false;
    const auto source=keyboard.elapsed_source([&] {
        const auto now=time+(stagger ? std::int64_t(reads)*100000 : 0);++reads;++total_reads;
        return now;
    },[&](pc98_input::Operation) {
        time=polls<2 ? 600000 : polls==2 ? 500600000 : polls<5 ? 501500000 : 503000000;
        stagger=polls==2;++polls;reads=0;
    });
    std::vector<std::uint16_t> words;
    const pc98_input::Observer witness=[&](const pc98_input::Observation& sample) {
        require_view(reads==9,"live frontend must consume eight bytes then Shift");
        if(words.size()==2)require_view(!sample.physical.keys[5] && keyboard.device().matrix()[5]==2,
            "tail must retain its actual Shot read across a later make");
        words.push_back(sample.after.actions);
    };
    const auto step=[&] {elapsed.advance_sampled(0,false,source,false,witness);};
    step();require_view(elapsed.main_state().player_input()==32 && !elapsed.main_state().consumed_input(),
        "elapsed keyboard player/tail distinction");
    step();require_view(elapsed.main_state().player_input()==32 && elapsed.main_state().consumed_input()==32,
        "elapsed keyboard later make");
    keyboard.focus(false,502000000);
    step();require_view(elapsed.main_state().player_input()==32 && !elapsed.main_state().consumed_input(),
        "focus release must preserve Sense until the game resets");
    step();require_view(!elapsed.main_state().player_input() && !elapsed.sampled_input().actions,
        "focus release must reach the next actual player update");
    require_view(words==std::vector<std::uint16_t>({32,32,0,32,32,32,0,0,0}) && total_reads==81,
        "complete elapsed frontend poll witness");
    std::ofstream elapsed_result(directory/"elapsed-result.txt");
    elapsed_result<<"elapsed_frontend=pass frames=4 polls="<<polls<<" scalar_and_shift_reads="<<total_reads
        <<" final_matrix_shortcut_rejected=1 focus_release=1\n";

    const auto joystick_exercise=[&](bool observed) {
        FrontEnd joystick(background,numerals,labels,cursors,selection_background,portraits,&assets);
        joystick.enable_registration();joystick.input(menu::Input::confirm);
        joystick.input(menu::Input::confirm);joystick.input(menu::Input::confirm);
        require_view(joystick.live_main(),"live joystick frontend did not enter MAIN");
        const std::array<unsigned,8> groups{{7,9,8,5,2,0,3,6}};
        const std::array<std::uint8_t,9> pins{{0xf7,0xff,0xff,0xfd,0xff,0xdf,0xff,0,0}};
        const std::vector<std::uint16_t> expected{8,8,0,2,0,32,0,0,0};
        unsigned polls=0,current=0,phase=0,enables=0,pin_reads=0,observations=0;
        std::vector<std::uint16_t> words;std::ostringstream samples;
        pc98_input::ByteSource source{[&](pc98_input::Operation) {
            require_view(polls<pins.size(),"unexpected live joystick poll");current=polls++;phase=0;
        },[&](unsigned group) {
            require_view(phase<8 && group==groups[phase++],"live joystick keyboard byte order");
            return std::uint8_t(0);
        },[&] {
            require_view(phase++==8,"Shift must precede the joystick transaction");return false;
        },[&] {
            require_view(phase++==9,"joystick enable query order");++enables;return current<7;
        },[&] {
            require_view(phase++==10 && current<7,"disabled joystick performed a bus transaction");
            ++pin_reads;return pins[current];
        }};
        const pc98_input::Observer witness=[&](const pc98_input::Observation& sample) {
            require_view(observations==current && phase==(current<7?11u:10u),"joystick observer poll boundary");
            require_view(sample.physical.keys==pc98_input::BiosKeys{} &&
                sample.physical.joystick_enabled==(current<7) &&
                sample.physical.joystick_pins==(current<7?pins[current]:0xff),"joystick physical observation");
            require_view(sample.after.actions==expected.at(current),"joystick actual frontend latch");
            words.push_back(sample.after.actions);++observations;
            samples<<(sample.operation==pc98_input::Operation::reset?'R':'S')<<" 00000000000000000000 "
                <<sample.physical.shift<<' '<<sample.physical.joystick_enabled<<' '
                <<unsigned(sample.physical.joystick_pins)<<' '<<sample.after.actions<<' '<<sample.after.shift<<'\n';
        };
        const auto step=[&]{joystick.advance_sampled(0,false,source,false,observed?witness:pc98_input::Observer{});};
        step();require_view(joystick.main_state().player_input()==8 && !joystick.main_state().consumed_input(),
            "live joystick Right must survive release until the tail Reset");
        const auto position=joystick.main_state().player().position().current;
        require_view(position.x==192*16+64 && position.y==320*16,"live joystick Right player movement");
        step();require_view(joystick.main_state().player_input()==2 &&
            joystick.main_state().player().position().current.y==position.y+64,"live joystick Down player movement");
        step();require_view(joystick.main_state().player_input()==32,"live joystick Shot reaches MAIN");
        step();require_view(!joystick.main_state().player_input() && !joystick.sampled_input().actions,
            "disabled live joystick leaves no pending game action");
        require_view(polls==9 && enables==9 && pin_reads==7 && (!observed || words==expected),"complete live joystick read witness");
        std::ostringstream state;th04::portable::demo_wire::pools(state,0,joystick.main_state(),stage::Program(assets.standard));
        state<<joystick.process_random_state()<<' '<<joystick.process_random_draws()<<' '<<joystick.main_state().frames();
        for(const auto byte:joystick.main_state().random_ring_bytes())state.put(char(byte));
        if(observed) {
            std::ofstream output(directory/"joystick-polls.txt");output<<samples.str();
        }
        return state.str();
    };
    const auto joystick_baseline=joystick_exercise(false),joystick_observed=joystick_exercise(true);
    require_view(joystick_baseline==joystick_observed,"joystick observer changed complete pools/frame/RNG");
    std::ofstream joystick_result(directory/"joystick-result.txt");
    joystick_result<<"joystick_frontend=pass frames=4 polls=9 enable_reads=9 pin_reads=7 observer_equal=1\n";

    const auto host_exercise=[&](bool observed) {
        struct Controller final:host_joystick::Device {
            host_joystick::Sample sample{31,0xff};unsigned reads=0;
            host_joystick::Sample read() override {++reads;return sample;}
        };
        auto device=std::make_unique<Controller>();auto* raw=device.get();
        host_joystick::Joystick controller(std::move(device));
        FrontEnd scene(background,numerals,labels,cursors,selection_background,portraits,&assets);
        scene.enable_registration();controller.update(true);
        for(unsigned confirmation=0;confirmation<3;++confirmation) {
            raw->sample.pins=0xdf;controller.update(true);
            require_view(!joystick_menu(scene,controller),"controller menu unexpectedly exited");
            raw->sample.pins=0xff;controller.update(true);
        }
        require_view(scene.live_main(),"host controller did not enter MAIN through menus");
        raw->reads=0;
        const std::array<std::uint8_t,9> pins{{0xf7,0xff,0xff,0xfd,0xff,0xdf,0xff,0,0}};
        const std::vector<unsigned> expected{8,8,0,2,0,32,0,0,0};
        unsigned polls=0,current=0,observations=0;std::ostringstream samples;
        pc98_input::ByteSource keyboard{[&](pc98_input::Operation) {
            require_view(polls<pins.size(),"unexpected host controller poll");current=polls++;
            raw->sample={current<7?31:-1,pins[current]};
        },[](unsigned){return std::uint8_t(0);},[]{return false;}};
        const auto source=controller.source(keyboard,[]{return true;});
        const pc98_input::Observer witness=[&](const pc98_input::Observation& sample) {
            require_view(observations++==current && sample.after.actions==expected.at(current),"host controller actual latch");
            require_view(sample.physical.joystick_enabled==(current<8) &&
                sample.physical.joystick_pins==(current<7?pins[current]:0xff),"host unplug transaction boundary");
            samples<<(sample.operation==pc98_input::Operation::reset?'R':'S')<<' '
                <<std::string(20,'0')<<' '<<sample.physical.shift<<' '<<sample.physical.joystick_enabled<<' '
                <<unsigned(sample.physical.joystick_pins)<<' '<<sample.after.actions<<' '<<sample.after.shift<<'\n';
        };
        const auto step=[&]{scene.advance_sampled(controller.host_actions(),false,source,false,observed?witness:pc98_input::Observer{});};
        step();require_view(scene.main_state().player_input()==8,"host controller Right did not reach player");
        auto position=scene.main_state().player().position().current;
        require_view(position.x==192*16+64 && position.y==320*16,"host controller Right movement");
        step();require_view(scene.main_state().player_input()==2 &&
            scene.main_state().player().position().current.y==position.y+64,"host controller Down movement");
        step();require_view(scene.main_state().player_input()==32,"host controller Shot did not reach MAIN");
        step();require_view(!scene.main_state().player_input() && !scene.sampled_input().actions,"unplugged host controller retained action");
        require_view(polls==9 && raw->reads==8 && (!observed || observations==9),"host controller complete read extent");
        std::ostringstream state;th04::portable::demo_wire::pools(state,0,scene.main_state(),stage::Program(assets.standard));
        state<<scene.process_random_state()<<' '<<scene.process_random_draws()<<' '<<scene.main_state().frames();
        for(const auto byte:scene.main_state().random_ring_bytes())state.put(char(byte));
        if(observed){std::ofstream output(directory/"host-joystick-polls.txt");output<<samples.str();}
        return state.str();
    };
    const auto host_baseline=host_exercise(false),host_observed=host_exercise(true);
    require_view(host_baseline==host_observed,"host controller observer changed pools/frame/RNG");
    std::ofstream host_result(directory/"host-joystick-result.txt");
    host_result<<"host_joystick_frontend=pass menu_confirms=3 frames=4 polls=9 pin_reads=8 observer_equal=1\n";
}

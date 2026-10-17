// Original-input ordinary MAIN trace through the real FrontEnd dialogue owner.
// Menu counter and blocking input are explicit component stimuli, not timing claims.
void run_ordinary_front_trace(const PiImage& background,const CdgSheet& numerals,
    const CdgSheet& labels,const CdgSheet& cursors,const PiImage& selection_background,
    const CdgSheet& portraits,const MainAssets& assets) {
    namespace fs=std::filesystem;
    const fs::path output(assets.ordinary_trace_checks);
    require_view(!fs::exists(output),"fresh ordinary FrontEnd output required");
    std::ifstream plan(fs::path(assets.save_directory)/"ordinary-inputs.txt");
    unsigned seed,updates,character,shot_type;
    require_view(bool(plan>>seed>>updates>>character>>shot_type) && seed<600 && updates>0 && updates<=65535 && character<2 && shot_type<2,
                 "ordinary FrontEnd plan header");
    std::vector<unsigned> picture_frames{74,90,98,99,100,105,106,107,110,192,265,266,270,280,290,296,297,298,299,6549,6573,6574,6581,6582,6583,6740,6741,6753,6765,6772,6773,6774,7639,7641,7648,7657,7705,7770};
    std::ifstream picture_plan(fs::path(assets.save_directory)/"ordinary-picture-frames.txt");
    if(picture_plan) {
        picture_frames.clear();unsigned picture;
        while(picture_plan>>picture) {
            require_view(picture>0 && picture<=updates && (picture_frames.empty() || picture>picture_frames.back()),"ordinary picture frame order/extent");
            picture_frames.push_back(picture);
        }
        require_view(picture_plan.eof() && !picture_frames.empty(),"ordinary picture plan syntax/extent");
    }
    std::ifstream display_times(fs::path(assets.save_directory)/"ordinary-display-times.txt");
    const bool recorded_display=bool(display_times);
    std::uint64_t display_ns=0;
    if(recorded_display) {
        std::string magic;unsigned version,extent;std::uint64_t period;
        require_view(bool(display_times>>magic>>version>>extent>>period) && magic=="TH04_DISPLAY_NS" &&
            version==1 && extent==updates && period==std::uint64_t(frame_period.count()),"recorded display header/period/extent");
    }
    fs::create_directories(output);
    std::ofstream owners(output/"owners.txt"),go_blocks(output/"gameover-blocks.txt"),go_events(output/"gameover-events.txt");
    std::ofstream state(output/"state.txt"),consumed(output/"consumed.txt"),blocks(output/"blocks.txt"),pools(output/"pools.bin",std::ios::binary);
    std::ofstream homing(output/"homing.txt");require_view(bool(homing),"ordinary homing output unavailable");
    require_view(bool(go_blocks) && bool(go_events) && bool(owners) && bool(state) && bool(consumed) && bool(blocks) && bool(pools),"ordinary FrontEnd output unavailable");
    pools.write("TH04OP1\n",8);
    std::ofstream popup_rows(output/"popup-rows.bin",std::ios::binary);
    require_view(bool(popup_rows),"ordinary popup rows unavailable");popup_rows.write("TH04PU1\n",8);
    std::ofstream title_rows(output/"title-rows.bin",std::ios::binary);
    require_view(bool(title_rows),"ordinary title rows unavailable");title_rows.write("TH04TI1\n",8);
    FrontEnd scene(background,numerals,labels,cursors,selection_background,portraits,&assets,gameplay::Mode::ordinary);
    if(fs::exists(fs::path(assets.save_directory)/"stage-epoch-clear.txt"))
        require_view(fs::exists(fs::path(assets.save_directory)/"stage-epoch-plan.txt") &&
            fs::exists(fs::path(assets.save_directory)/"stage-epoch-waits.txt"),"epoch clear requires stage and wait inputs");
    if(recorded_display) {
        require_view(scene.text_refreshes()==1,"recorded display requires the common first refresh");
        scene.observe_text_time(0);
    }
    if(fs::exists(fs::path(assets.save_directory)/"stage-epoch-plan.txt")) {
        if(fs::exists(fs::path(assets.save_directory)/"stage-epoch-clear.txt"))scene.enable_elly();
        else if(fs::exists(fs::path(assets.save_directory)/"stage-epoch-waits.txt"))scene.enable_kurumi();
        else scene.enable_stage2();
    }
    scene.enable_configuration();scene.enable_registration();
    for(unsigned i=0;i<seed;++i)scene.advance(0,false,false);
    scene.input(menu::Input::confirm);if(character)scene.input(menu::Input::right);
    scene.input(menu::Input::confirm);if(shot_type)scene.input(menu::Input::down);scene.input(menu::Input::confirm);
    require_view(scene.live_main() && scene.main_state().mode()==gameplay::Mode::ordinary && scene.resident().random_seed_source==seed,
                 "ordinary FrontEnd MAIN start/seed");
    scene.set_gameover_observer([&](const gameover::Event& event) {
        go_events<<scene.main_state().frames()<<' '<<unsigned(event.kind)<<' '<<event.left<<' '<<event.row<<' '
            <<event.value<<' '<<event.attribute<<' '<<std::quoted(event.text)<<'\n';
    });
    const stage::Program program(assets.standard);
    std::ofstream popup_state(output/"popup-state.txt");require_view(bool(popup_state),"ordinary popup state unavailable");
    std::ofstream title_state(output/"title-state.txt");require_view(bool(title_state),"ordinary title state unavailable");
    scene.main_state().set_actor_observer([&](const gameplay::State& s){
        th04::portable::demo_wire::pools(pools,0,s,program);
        const auto& p=s.popup_state();
        popup_state<<s.frames()<<' '<<+p.frame<<' '<<p.length<<' '<<+p.current<<' '<<p.reached<<' '
            <<p.left<<' '<<p.destination<<' '<<+p.requested<<' '<<(p.active ? 0x67e8 : 0x11be)<<' '<<p.bonus<<' ';
        for(auto b:p.shift)popup_state<<std::hex<<std::setfill('0')<<std::setw(2)<<+b;
        popup_state<<std::dec<<'\n';
        const auto& t=s.title_state();
        const auto callback=s.overlay().callback;
        const unsigned pointer=callback==transition::Callback::enter ? 0x62b3 : callback==transition::Callback::leave ? 0x6349 : callback==transition::Callback::titles ? 0x6446 : callback==transition::Callback::boss_titles ? 0x66a5 : 0x11be;
        title_state<<s.frames()<<' '<<+s.overlay().time<<' '<<pointer<<' '<<+t.frame<<' '<<+t.boss_frame<<' '<<+t.sprite<<' '<<+t.stage_id<<' '<<+t.bgm_id<<' '<<t.stage_length<<' '<<t.bgm_length<<' '<<t.boss_length;
        for(const auto& d:s.title_draws())title_state<<'|'<<d.left<<' '<<d.top<<' '<<+d.sprite<<' '<<+d.color;
        title_state<<'\n';
    });
    const auto base_draws=scene.process_random_draws(),base_samples=scene.main_state().random_samples();
    const auto hex=[&](const auto& bytes){constexpr char digits[]="0123456789abcdef";for(auto value:bytes)state<<digits[unsigned(value)>>4]<<digits[unsigned(value)&15];};
    state<<"TH04_ORDINARY_STATE 1 "<<updates<<'\n';
    std::ofstream display_clock(output/"display-clock.txt");require_view(bool(display_clock),"display clock output unavailable");
    display_clock<<"TH04_DISPLAY_CLOCK 1 "<<updates<<' '<<frame_period.count()<<' '<<recorded_display<<'\n';
    unsigned blocked_ticks=0,dialog_ticks=0;bool prefix_saved=false;
    for(unsigned frame=0;frame<=updates;++frame) {
        unsigned number,keys,shift;
        require_view(bool(plan>>number>>keys>>shift) && number==frame && keys<=65535 && !(keys&~0x303fu) && shift<=1,"ordinary FrontEnd input/order/width");
        auto& main=scene.main_state();require_view(main.frames()==frame,"ordinary FrontEnd missing update");
        if(recorded_display && frame) {
            unsigned sample;std::uint64_t now;
            require_view(bool(display_times>>sample>>now) && sample==frame && now>display_ns &&
                now<=std::uint64_t(INT64_MAX),"recorded display time order/width");
            display_ns=now;scene.observe_text_time(std::int64_t(now));
        }
        display_clock<<frame<<' '<<display_ns<<' '<<scene.text_refreshes()<<' '<<scene.text_blink_visible()<<'\n';
        const auto& life=main.life();const auto pos=main.player().position().current;
        const auto target=main.homing_target().value_or(th04::portable::motion::Point{-15984,-15984});
        homing<<frame<<' '<<target.x<<' '<<target.y<<'\n';
        const auto& scoreboard=main.scoreboard();const auto& resident=scene.resident();
        state<<frame<<' '<<(frame==updates ? 'P':'I')<<' '<<keys<<' '<<shift<<' '<<+resident.stage<<' ';hex(scoreboard.digits);
        state<<' '<<main.score().score_delta<<' '<<scoreboard.frame_delta<<' '<<scene.process_random_state()<<' ';hex(main.random_ring_bytes());
        state<<' '<<main.random_cursor()<<' '<<pos.x<<' '<<pos.y<<' '<<+main.score().power<<' '<<+life.hit<<' '<<+life.invincibility<<' '<<+life.respawn_time
             <<' '<<+main.score().remaining_lives<<' '<<+main.score().remaining_bombs<<' '<<+resident.miss_count<<' '<<+resident.bombs_used
             <<' '<<scene.process_random_draws()-base_draws<<' '<<main.random_samples()-base_samples<<'\n';
        const auto& boss=main.boss_snapshot();
        th04::portable::demo_wire::Writer owner;
        owner.movement(boss.position);owner.word(boss.hp);owner.byte(boss.sprite);owner.byte(boss.phase);
        owner.word(boss.phase_frame);owner.byte(boss.damage);owner.byte(boss.mode);owner.byte(boss.angle);
        owner.byte(boss.patterns_or_bonus);owner.word(boss.end_hp);
        for(auto byte:boss.additional)owner.byte(byte);
        owner.point(boss.hitbox_radius);owner.byte(boss.timed_out);
        require_view(owner.data.size()==45,"ordinary Boss owner wire extent");
        owners<<frame<<' ';constexpr char owner_digits[]="0123456789abcdef";
        for(auto byte:owner.data)owners<<owner_digits[byte>>4]<<owner_digits[byte&15];
        owners<<'\n';
        const auto text=main_text_plane(main).physical_bytes(0xa0000,0x4000);
        const std::uint32_t observed_frame=frame;popup_rows.write(reinterpret_cast<const char*>(&observed_frame),4);
        for(unsigned row:{2u,23u})for(unsigned bank:{0u,0x2000u})
            popup_rows.write(reinterpret_cast<const char*>(text.data()+bank+row*160u),160);
        {
            if(std::find(picture_frames.begin(),picture_frames.end(),frame)!=picture_frames.end()) {
                const auto random=scene.process_random_state();const auto samples=main.random_samples();
                const auto cursor=main.random_cursor();
                std::ostringstream before;th04::portable::demo_wire::pools(before,0,main,program);
                scene.repaint();const auto pictured=scene.frame();scene.repaint();
                std::ostringstream after;th04::portable::demo_wire::pools(after,0,main,program);
                require_view(main.frames()==frame && scene.process_random_state()==random && main.random_samples()==samples &&
                    main.random_cursor()==cursor && before.str()==after.str() && pictured.pixels==scene.frame().pixels &&
                    pictured.indices==scene.frame().indices,"title repaint advanced state or changed the picture");
                write_bmp((output/("title-"+std::to_string(frame)+".bmp")).string(),pictured);
                require_view(pictured.indices.size()==640*400,"title graphics observation extent");
                std::ofstream graphics(output/("title-"+std::to_string(frame)+"-graphics.bin"),std::ios::binary);
                graphics.write(reinterpret_cast<const char*>(pictured.indices.data()),pictured.indices.size());
                std::ofstream tram(output/("title-"+std::to_string(frame)+"-text.bin"),std::ios::binary);
                tram.write(reinterpret_cast<const char*>(text.data()),text.size());
            }
        }
        if(frame==7639 || frame==7641 || frame==7648 || frame==7657 || frame==7705 || frame==7770) {
            scene.repaint();write_bmp((output/("popup-"+std::to_string(frame)+".bmp")).string(),scene.frame());
            std::ofstream snapshot(output/("popup-"+std::to_string(frame)+"-text.bin"),std::ios::binary);
            snapshot.write(reinterpret_cast<const char*>(text.data()),text.size());
            require_view(main.frames()==frame,"popup observation advanced the simulation");
        }
        {
            const auto tram=main_text_plane(main).physical_bytes(0xa0000,16384);
            const std::uint32_t number=frame;title_rows.write(reinterpret_cast<const char*>(&number),4);
            for(unsigned row:{11u,13u,23u}) {
                title_rows.write(reinterpret_cast<const char*>(tram.data()+row*160),160);
                title_rows.write(reinterpret_cast<const char*>(tram.data()+8192+row*160),160);
            }
        }
        if(frame==updates)break;
        const auto held=std::uint16_t((keys&0x2fu)|(keys&0x10u ? 0x800u : 0)|(keys&0x1000u ? 0x2000u : 0)|(keys&0x2000u ? 0x1000u : 0));
        require_view(player::input_from_host_actions(held)==keys,"ordinary FrontEnd host input translation");
        std::optional<std::uint16_t> suspended_player_sample;
        for(unsigned attempt=0;;++attempt) {
            require_view(attempt<10000 && scene.live_main() && !scene.pause_active(),"unconfigured ordinary FrontEnd blocking owner");
            const bool dialog=scene.dialog_active();const auto status=scene.dialog_status();
            const auto* go=main.game_over();const int go_before=go ? int(go->phase()) : -1;
            auto input=dialog ? std::uint16_t((status==th04::portable::dialog::Status::press || status==th04::portable::dialog::Status::running) ? 0x1000 : 0) : held;
            if(go) {
                const bool wait=go->phase()==gameover::Phase::press || go->phase()==gameover::Phase::menu;
                input=std::uint16_t(wait && attempt%20<10 ? 0x1000 : 0);
            }
            scene.advance(input,shift!=0,false);
            if(!go && main.game_over()) {
                // player_update consumed this argument before its miss helper
                // entered Game Over. Later UI polls resume a suffix, not a new player prefix.
                require_view(!suspended_player_sample,"duplicate suspended player prefix");
                suspended_player_sample=main.consumed_input();
            }
            if(go_before>=0 || main.game_over()) {
                go_blocks<<frame<<' '<<attempt<<' '<<go_before<<' '<<(main.game_over() ? int(main.game_over()->phase()) : -1)
                    <<' '<<input<<' '<<main.frames()<<' '<<main.consumed_input()<<' '
                    <<suspended_player_sample.value_or(main.consumed_input())<<' '<<+main.score().remaining_lives<<' '
                    <<+scene.resident().miss_count<<' '<<+main.scoreboard().digits[0]<<'\n';
            }
            if(dialog || scene.dialog_active()) {blocks<<frame<<' '<<attempt<<' '<<unsigned(status)<<' '<<input<<' '<<main.frames()<<' '<<scene.dialog_offset()<<'\n';++dialog_ticks;}
            if(!prefix_saved && scene.dialog_active() && scene.dialog_status()==th04::portable::dialog::Status::running && scene.dialog_offset()==0) {
                const auto random=scene.process_random_state();const auto cursor=main.random_cursor();
                const auto pos=main.player().position().current;
                std::ofstream checkpoint(output/"dialog-prefix.txt");
                checkpoint<<frame<<' '<<pos.x<<' '<<pos.y<<' '<<+main.shots().snapshot().time<<' '
                    <<+main.life().invincibility<<' '<<+main.life().respawn_time<<' '<<+main.life().hit<<' '
                    <<+main.life().miss_time<<' '<<random<<' '<<cursor<<'\n';
                std::ofstream snapshot(output/"dialog-prefix-pools.bin",std::ios::binary);
                snapshot.write("TH04OD1\n",8);th04::portable::demo_wire::pools(snapshot,0,main,program);
                scene.repaint();write_bmp((output/"dialog-prefix.bmp").string(),scene.frame());
                require_view(main.frames()==frame && scene.process_random_state()==random && main.random_cursor()==cursor,
                             "dialogue prefix repaint advanced gameplay or RNG");
                prefix_saved=true;
            }
            if(main.frames()!=frame)break;
            ++blocked_ticks;
        }
        if(suspended_player_sample)require_view(*suspended_player_sample==main.player_input(),"Game Over repeated or changed the player prefix");
        consumed<<frame<<' '<<main.player_input()<<' '<<shift<<'\n';
        require_view(main.frames()==frame+1 && scene.resident().stage==0,"ordinary FrontEnd crossed stage extent");
    }
    plan>>std::ws;require_view(plan.peek()==std::char_traits<char>::eof(),"ordinary FrontEnd trailing input");
    if(recorded_display) {
        display_times>>std::ws;
        require_view(display_times.peek()==std::char_traits<char>::eof(),"recorded display trailing time");
    }
    std::ofstream result(output/"result.txt");result<<"updates "<<updates<<" blocked_ticks "<<blocked_ticks<<" dialog_ticks "<<dialog_ticks<<'\n';
#include "stage_epoch_trace.inl"
}

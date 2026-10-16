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
    fs::create_directories(output);
    std::ofstream owners(output/"owners.txt");
    std::ofstream state(output/"state.txt"),consumed(output/"consumed.txt"),blocks(output/"blocks.txt"),pools(output/"pools.bin",std::ios::binary);
    require_view(bool(owners) && bool(state) && bool(consumed) && bool(blocks) && bool(pools),"ordinary FrontEnd output unavailable");
    pools.write("TH04OP1\n",8);
    FrontEnd scene(background,numerals,labels,cursors,selection_background,portraits,&assets,gameplay::Mode::ordinary);
    scene.enable_configuration();scene.enable_registration();
    for(unsigned i=0;i<seed;++i)scene.advance(0,false,false);
    scene.input(menu::Input::confirm);if(character)scene.input(menu::Input::right);
    scene.input(menu::Input::confirm);if(shot_type)scene.input(menu::Input::down);scene.input(menu::Input::confirm);
    require_view(scene.live_main() && scene.main_state().mode()==gameplay::Mode::ordinary && scene.resident().random_seed_source==seed,
                 "ordinary FrontEnd MAIN start/seed");
    const stage::Program program(assets.standard);
    scene.main_state().set_actor_observer([&](const gameplay::State& s){th04::portable::demo_wire::pools(pools,0,s,program);});
    const auto base_draws=scene.process_random_draws(),base_samples=scene.main_state().random_samples();
    const auto hex=[&](const auto& bytes){constexpr char digits[]="0123456789abcdef";for(auto value:bytes)state<<digits[unsigned(value)>>4]<<digits[unsigned(value)&15];};
    state<<"TH04_ORDINARY_STATE 1 "<<updates<<'\n';
    unsigned blocked_ticks=0,dialog_ticks=0;bool prefix_saved=false;
    for(unsigned frame=0;frame<=updates;++frame) {
        unsigned number,keys,shift;
        require_view(bool(plan>>number>>keys>>shift) && number==frame && keys<=65535 && !(keys&~0x303fu) && shift<=1,"ordinary FrontEnd input/order/width");
        auto& main=scene.main_state();require_view(main.frames()==frame,"ordinary FrontEnd missing update");
        const auto& life=main.life();const auto pos=main.player().position().current;
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
        if(frame==updates)break;
        const auto held=std::uint16_t((keys&0x2fu)|(keys&0x10u ? 0x800u : 0)|(keys&0x1000u ? 0x2000u : 0)|(keys&0x2000u ? 0x1000u : 0));
        require_view(player::input_from_host_actions(held)==keys,"ordinary FrontEnd host input translation");
        for(unsigned attempt=0;;++attempt) {
            require_view(attempt<10000 && scene.live_main() && !main.game_over(),"unconfigured ordinary FrontEnd blocking owner");
            const bool dialog=scene.dialog_active();const auto status=scene.dialog_status();
            const auto input=dialog ? std::uint16_t((status==th04::portable::dialog::Status::press || status==th04::portable::dialog::Status::running) ? 0x1000 : 0) : held;
            scene.advance(input,shift!=0,false);
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
        consumed<<frame<<' '<<main.consumed_input()<<' '<<shift<<'\n';
        require_view(main.frames()==frame+1 && scene.resident().stage==0,"ordinary FrontEnd crossed stage extent");
    }
    plan>>std::ws;require_view(plan.peek()==std::char_traits<char>::eof(),"ordinary FrontEnd trailing input");
    std::ofstream result(output/"result.txt");result<<"updates "<<updates<<" blocked_ticks "<<blocked_ticks<<" dialog_ticks "<<dialog_ticks<<'\n';
}

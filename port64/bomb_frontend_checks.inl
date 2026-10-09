// Actual OP selection, held X and finite STD contact. Original pixel replay
// receives explicitly captured pre-Bomb display/state, never a forced hit.
void run_bomb_checks(const PiImage& background,const CdgSheet& numerals,
    const CdgSheet& labels,const CdgSheet& cursors,const PiImage& selection_background,
    const CdgSheet& portraits,const MainAssets& assets,const std::string& destination) {
    namespace fs=std::filesystem;
    const fs::path directory(destination);
    require_view(!fs::exists(directory) && assets.muted,"use fresh muted Bomb controls");
    fs::create_directories(directory);
    std::ofstream journal(directory/"trace.txt",std::ios::binary),records(directory/"frames.txt",std::ios::binary),
        snapshots(directory/"snapshots.txt",std::ios::binary);
    struct Restore {std::streambuf* old;~Restore(){std::cout.rdbuf(old);}} restore{std::cout.rdbuf(journal.rdbuf())};
    std::ostream binary(restore.old);
#ifdef _WIN32
    _setmode(_fileno(stdout),_O_BINARY);
#endif
    const auto life=[](const player::LifeState& s) {
        std::vector<int> v{s.invincibility,s.hit,s.miss_time,s.respawn_time,s.explosion_radius,
            s.explosion_angle,s.misses,s.bombs_used,s.quit,s.bombing,s.bomb_frame,s.bombing_disabled,
            s.clear_time,s.pull_items,s.scroll_active,s.background,s.circle_color,s.palette_tone,s.palette_changed};
        for(auto x:s.palette14)v.push_back(x);
        for(auto x:s.palette_backup)v.push_back(x);
        return v;
    };
    const auto hex=[](const Bytes& bytes) {
        std::ostringstream out;out<<std::hex<<std::setfill('0');
        for(auto x:bytes)out<<std::setw(2)<<unsigned(x);
        return out.str();
    };
    const auto word=[](Bytes& v,int x) {v.push_back(std::uint8_t(x));v.push_back(std::uint8_t(unsigned(x)>>8));};
    const auto stars=[&](const bomb::Snapshot& s) {
        Bytes v;for(const auto& x:s.stars) {word(v,x.center.x);word(v,x.center.y);v.push_back(x.angle);v.push_back(x.speed);}return v;
    };
    const auto circles=[&](const circle::Snapshot& s) {
        Bytes v;for(const auto& x:s.entities) {v.push_back(x.flag);v.push_back(x.age);word(v,x.center.x);word(v,x.center.y);word(v,x.radius);word(v,x.delta);}return v;
    };
    Bytes standard{0,0,8};standard.insert(standard.end(),8,0);standard.push_back(9);
    standard.insert(standard.end(),8,16);standard.push_back(0);
    for(auto x:{1,9,0x10,128,1,0,0,0,6,100,0,0})standard.push_back(std::uint8_t(x));
    for(unsigned frame:{64u,2000u}) {
        word(standard,frame);standard.push_back(1);standard.push_back(0);word(standard,3072);
        word(standard,5120);standard.insert(standard.end(),{255,0,0});
    }
    standard.insert(standard.end(),{0,0});const auto extent=standard.size()-2;
    standard[0]=std::uint8_t(extent);standard[1]=std::uint8_t(extent>>8);
    std::ofstream std_file(directory/"finite.std",std::ios::binary);
    std_file.write(reinterpret_cast<const char*>(standard.data()),standard.size());
    const std::array<unsigned,21> checkpoints{0,1,7,31,32,47,48,49,50,80,81,84,119,120,160,175,176,177,178,225,226};
    for(unsigned character=0;character<2;++character)for(unsigned profile=0;profile<3;++profile)
        for(unsigned paint=0;paint<2;++paint) {
        const auto name="c"+std::to_string(character)+"-p"+std::to_string(profile)+"-paint"+std::to_string(paint);
        auto input=assets;input.standard=standard;
        FrontEnd scene(background,numerals,labels,cursors,selection_background,portraits,&input);
        scene.input(menu::Input::confirm);if(character)scene.input(menu::Input::right);
        scene.input(menu::Input::confirm);scene.input(menu::Input::confirm);
        scene.enable_bomb_capture();auto& main=scene.main_state();
        player::LifeState before;Bytes old_ring,old_stars,old_circles;
        unsigned cursor=0,stage_frame=0;
        main.set_bomb_observer([&](const auto& l,const auto& random,const auto& effect,const auto& pool,std::uint16_t frame) {
            before=l;cursor=random.cursor();stage_frame=frame;
            old_ring.assign(random.bytes().begin(),random.bytes().end());
            old_stars=stars(effect.snapshot());old_circles=circles(pool.snapshot());
        });
        bool started=false,late_rejected=false;unsigned steps=0;
        for(unsigned clock=0;clock<650;++clock) {
            bool press=false;
            if(!profile)press=clock==32;
            else if(profile==1)press=main.life().miss_time>32;
            else if(main.life().miss_time==32) {press=true;late_rejected=true;}
            else if(late_rejected && !main.life().miss_time && !started)press=true;
            std::uint16_t keys=press ? 0x800 : 0;
            if(started && main.life().bomb_frame<170)keys|=0x800; // Held X cannot restart an active Bomb.
            if(started && main.life().bomb_frame>60 && main.life().bomb_frame<100)keys|=player::left;
            scene.advance(keys,false,paint!=0);
            if(profile==2 && main.life().miss_time==31)
                require_view(!main.life().bombing && main.life().bombs_used==0,"late deathbomb escaped the32 boundary");
            if(!main.bomb_frame().active)continue;
            started=true;++steps;const auto& plan=main.bomb_frame();
            const auto life_after=life(main.life());
            records<<name<<' '<<character<<' '<<unsigned(plan.frame)<<' '<<stage_frame<<' '
                <<plan.scroll_line<<' '<<cursor<<' '<<plan.retain_background;
            for(auto v:life(before))records<<' '<<v;
            for(auto v:life_after)records<<' '<<v;
            records<<' '<<main.random_cursor()<<' '<<hex(old_ring)<<' '<<hex(old_stars)<<' '<<hex(old_circles)<<' '
                <<hex(stars(main.bomb_effect().snapshot()))<<' '<<hex(circles(main.circles().snapshot()))<<'\n';
            if(std::find(checkpoints.begin(),checkpoints.end(),plan.frame)!=checkpoints.end()) {
                const auto random=main.random_cursor();const auto process=scene.process_random_state();
                scene.repaint();const auto once=scene.frame().pixels;const auto first=scene.bomb_capture();scene.repaint();
                const auto& capture=scene.bomb_capture();
                require_view(once==scene.frame().pixels && first.before==capture.before && first.after==capture.after &&
                    first.final==capture.final && first.rgb==capture.rgb && random==main.random_cursor() &&
                    process==scene.process_random_state() && life_after==life(main.life()),"Bomb repaint changed state/RNG/display");
                snapshots<<name<<' '<<unsigned(plan.frame)<<' '<<capture.display_line<<' '<<capture.page;
                for(auto v:capture.palette)snapshots<<' '<<unsigned(v);
                snapshots<<'\n';
                for(const auto* bytes:{&capture.before,&capture.after,&capture.final,&capture.rgb})
                    binary.write(reinterpret_cast<const char*>(bytes->data()),bytes->size());
                require_view(bool(binary),"Bomb capture output failed");
            }
            if(plan.frame==226)break;
        }
        require_view(started && steps==227 && !main.life().bombing && main.life().bomb_frame==227 &&
            main.life().bombs_used==1 && main.score().remaining_bombs==scene.resident().credit_bombs-1 &&
            main.life().misses==(profile==2 ? 1 : 0) && main.life().palette_tone==100 && main.life().scroll_active,
            "ordinary Bomb/deathbomb/late-Bomb route did not complete");
        journal<<name<<" steps="<<steps<<" misses="<<unsigned(main.life().misses)<<" rng="<<main.random_cursor()<<" muted=1\n";
    }
}

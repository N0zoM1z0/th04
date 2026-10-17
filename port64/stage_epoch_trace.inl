// Optional stage-boundary diagnostic. Inputs advance the normal scene;
// observations never assign gameplay state, random values or clock phase.
    if(fs::exists(fs::path(assets.save_directory)/"stage-epoch-plan.txt")) {
        require_view(updates==9835,"epoch fixture requires the attested preceding component extent");
        std::ifstream epoch_plan(fs::path(assets.save_directory)/"stage-epoch-plan.txt");
        std::string magic;unsigned version,extent,final_keys,final_shift;
        require_view(bool(epoch_plan>>magic>>version>>extent>>final_keys>>final_shift) &&
            magic=="TH04_STAGE_EPOCH" && version==1 && extent>0 && extent<=65535 && final_keys<=65535 && final_shift==0,"epoch fixture header/input");
        std::ifstream wait_plan(fs::path(assets.save_directory)/"stage-epoch-waits.txt");
        const bool wait_inputs=bool(wait_plan);
        std::ifstream clear_plan(fs::path(assets.save_directory)/"stage-epoch-clear.txt");
        const bool until_clear=bool(clear_plan);
        unsigned stage3_updates=0,stage3_keys=0,stage3_shift=0;
        bool extended_stage3=false;
        if(until_clear) {
            require_view(wait_inputs && bool(clear_plan>>magic>>version>>stage3_updates>>stage3_keys>>stage3_shift) &&
                magic=="TH04_STAGE_CLEAR" && (version==1 || version==2) && stage3_updates>0 &&
                stage3_updates<=65535 && (version==2 || stage3_updates==1) &&
                stage3_keys<=65535 && stage3_shift==0,"epoch clear plan header/input");
            extended_stage3=(version==2);
            if(!extended_stage3) {
                clear_plan>>std::ws;
                require_view(clear_plan.peek()==std::char_traits<char>::eof(),"epoch trailing clear input");
            }
        }
        std::vector<std::pair<unsigned,std::string>> wait_frames,observed_wait_frames;
        std::ofstream wait_blocks,player_samples;
        if(wait_inputs) {
            unsigned count;
            require_view(bool(wait_plan>>magic>>version>>count) && magic=="TH04_STAGE_WAITS" &&
                version==1 && count>0 && count<=16,"epoch wait plan header");
            for(unsigned i=0;i<count;++i) {
                unsigned frame;std::string kind;
                require_view(bool(wait_plan>>frame>>kind) && frame>0 && frame<extent &&
                    (kind=="dialogue" || kind=="continue") &&
                    (wait_frames.empty() || frame>wait_frames.back().first),"epoch wait cue kind/order/extent");
                wait_frames.emplace_back(frame,kind);
            }
            wait_plan>>std::ws;require_view(wait_plan.peek()==std::char_traits<char>::eof(),"epoch trailing wait cues");
            wait_blocks.open(output/"stage2-blocks.txt");player_samples.open(output/"stage2-consumed.txt");
            require_view(bool(wait_blocks)&&bool(player_samples),"epoch wait observations unavailable");
        }
        std::ofstream epoch(output/"stage-native.jsonl"),epoch_pools(output/"stage2-pools.bin",std::ios::binary),tail_pools(output/"stage1-tail-pools.bin",std::ios::binary);
        require_view(bool(epoch)&&bool(epoch_pools)&&bool(tail_pools),"epoch output unavailable");
        epoch_pools.write("TH04OP1\n",8);tail_pools.write("TH04OP1\n",8);
        const stage::Program stage2_program(assets.stage2.standard);
        std::optional<stage::Program> stage3_program;
        std::ofstream stage3_pools,stage3_player;
        if(until_clear) {
            stage3_program.emplace(assets.stage3.standard);
            stage3_pools.open(output/"stage3-pools.bin",std::ios::binary);
            stage3_player.open(output/"stage3-consumed.txt");
            require_view(bool(stage3_pools)&&bool(stage3_player),"epoch Stage3 output unavailable");
            stage3_pools.write("TH04OP1\n",8);
        }
        std::vector<std::pair<unsigned,std::string>> stage3_wait_frames,stage3_observed_wait_frames;
        std::ofstream stage3_blocks;
        std::ifstream stage3_wait_plan(fs::path(assets.save_directory)/"stage3-epoch-waits.txt");
        require_view(!stage3_wait_plan || extended_stage3,"epoch unused Stage3 wait plan");
        if(extended_stage3) {
            require_view(bool(stage3_wait_plan),"epoch Stage3 wait plan required");
            unsigned count;
            require_view(bool(stage3_wait_plan>>magic>>version>>count) && magic=="TH04_STAGE_WAITS" &&
                version==1 && count<=16,"epoch Stage3 wait header");
            for(unsigned i=0;i<count;++i) {
                unsigned frame;std::string kind;
                require_view(bool(stage3_wait_plan>>frame>>kind) && frame>0 && frame<stage3_updates &&
                    (kind=="dialogue" || kind=="continue") &&
                    (stage3_wait_frames.empty() || frame>stage3_wait_frames.back().first),
                    "epoch Stage3 wait kind/order/extent");
                stage3_wait_frames.emplace_back(frame,kind);
            }
            stage3_wait_plan>>std::ws;
            require_view(stage3_wait_plan.peek()==std::char_traits<char>::eof(),"epoch trailing Stage3 wait cues");
            stage3_blocks.open(output/"stage3-blocks.txt");
            require_view(bool(stage3_blocks),"epoch Stage3 wait output unavailable");
        }
        std::uint64_t ring_offset=0;unsigned ordinal=0;
        const auto observe=[&](const char* label,const gameplay::State& s) {
            const auto dump=[&](const auto& bytes){constexpr char digits[]="0123456789abcdef";for(auto v:bytes)epoch<<digits[unsigned(v)>>4]<<digits[unsigned(v)&15];};
            bool comma=false;
            const auto field=[&](const char* name,const auto& bytes) {if(comma)epoch<<',';comma=true;epoch<<'"'<<name<<"\":\"";dump(bytes);epoch<<'"';};
            const auto integer=[&](const char* name,std::uint64_t value,unsigned size) {std::vector<std::uint8_t> b;for(unsigned i=0;i<size;++i)b.push_back(std::uint8_t(value>>(i*8)));field(name,b);};
            if(wait_inputs && std::string(label)=="stage2-actor")player_samples<<s.frames()<<' '<<s.player_input()<<'\n';
            if(until_clear && std::string(label)=="stage3-actor")stage3_player<<s.frames()<<' '<<s.player_input()<<'\n';
            const auto& life=s.life();const auto& board=s.scoreboard();const auto& resident=scene.resident();
            epoch<<"{\"ordinal\":"<<ordinal++<<",\"label\":\""<<label<<"\",\"resource_stage\":"<<+resident.resource_stage<<",\"resident_stage\":"<<+resident.stage<<",\"fields\":{";
            integer("frame",s.frames(),2);integer("stage",resident.resource_stage,1);integer("input",s.consumed_input(),2);
            field("score_digits",board.digits);integer("score_delta",s.score().score_delta,4);integer("score_delta_frame",board.frame_delta,4);integer("lcg",scene.process_random_state(),4);field("ring",s.random_ring_bytes());integer("ring_cursor",s.random_cursor(),2);
            th04::portable::demo_wire::Writer position;position.point(s.player().position().current);field("player_pos",position.data);
            integer("power",s.score().power,1);integer("hit",life.hit,1);integer("invincibility",life.invincibility,1);integer("respawn",life.respawn_time,1);
            const auto& boss=s.boss_snapshot();th04::portable::demo_wire::Writer owner;owner.movement(boss.position);owner.word(boss.hp);owner.byte(boss.sprite);owner.byte(boss.phase);owner.word(boss.phase_frame);owner.byte(boss.damage);owner.byte(boss.mode);owner.byte(boss.angle);owner.byte(boss.patterns_or_bonus);owner.word(boss.end_hp);field("boss",owner.data);field("boss_statebyte",boss.additional);th04::portable::demo_wire::Writer hitbox;hitbox.point(boss.hitbox_radius);field("boss_hitbox_radius",hitbox.data);integer("boss_phase_timed_out",boss.timed_out,1);
            const auto& mid=s.midboss_state();th04::portable::demo_wire::Writer midboss_wire;
            midboss_wire.movement(mid.position);midboss_wire.word(mid.start_frame);midboss_wire.word(mid.hp);
            midboss_wire.byte(mid.sprite);midboss_wire.byte(mid.phase);midboss_wire.word(mid.phase_frame);
            midboss_wire.byte(mid.damaged);midboss_wire.byte(mid.unused_angle);
            field("midboss",midboss_wire.data);integer("midboss_active",mid.active,1);
            if(extended_stage3 && resident.resource_stage==2) {
                const auto* private_midboss=s.stage3_midboss();
                require_view(private_midboss!=nullptr,"epoch Stage3 private Midboss owner");
                const auto& private_state=private_midboss->snapshot();
                field("midboss3_private",std::array<std::uint8_t,3>{private_state.pattern,
                    private_state.mirror,private_state.patterns_done});
            }
            const auto target=s.homing_target().value_or(th04::portable::motion::Point{-15984,-15984});th04::portable::demo_wire::Writer homing;homing.point(target);field("homing",homing.data);
            epoch<<"},\"lives\":"<<+s.score().remaining_lives<<",\"bombs\":"<<+s.score().remaining_bombs<<",\"misses\":"<<+resident.miss_count<<",\"bombs_used\":"<<+resident.bombs_used<<",\"lcg_calls\":"<<scene.process_random_draws()-base_draws<<",\"ring_samples_since_fill\":"<<s.random_samples()<<",\"ring_calls\":"<<ring_offset+s.random_samples()-base_samples<<"}\n";
        };
        const auto translate=[](unsigned keys) {return std::uint16_t((keys&0x2fu)|(keys&0x10u?0x800u:0)|(keys&0x1000u?0x2000u:0)|(keys&0x2000u?0x1000u:0));};
        scene.main_state().set_actor_observer([&](const gameplay::State& s) {
            if(scene.resident().resource_stage==0) {th04::portable::demo_wire::pools(tail_pools,0,s,program);observe("stage1-actor",s);}
            else if(scene.resident().resource_stage==1) {th04::portable::demo_wire::pools(epoch_pools,0,s,stage2_program);observe("stage2-actor",s);}
            else {
                require_view(until_clear && scene.resident().resource_stage==2 && bool(stage3_program),"epoch unexpected actor resource owner");
                th04::portable::demo_wire::pools(stage3_pools,0,s,*stage3_program);observe("stage3-actor",s);
            }
        });
        unsigned guard=0;
        while(!scene.main_state().next_stage_requested()) {
            require_view(++guard<=16 && scene.live_main() && !scene.dialog_active(),"epoch departure did not complete naturally");
            scene.advance(translate(final_keys),false,false);observe("stage1-score",scene.main_state());
        }
        observe("stage1-return",scene.main_state());ring_offset=scene.main_state().random_samples();
        scene.set_stage_init_observer([&](const gameplay::State& s) {
            require_view(s.frames()==0,"epoch initialization frame");
            if(scene.resident().resource_stage==1) {
                th04::portable::demo_wire::pools(epoch_pools,0,s,stage2_program);observe("init_return",s);
            } else {
                require_view(until_clear && scene.resident().resource_stage==2 && bool(stage3_program),"epoch initialization boundary");
                th04::portable::demo_wire::pools(stage3_pools,0,s,*stage3_program);observe("stage3-init",s);
            }
        });
        unsigned completed=0;
        for(unsigned frame=0;frame<extent;++frame) {
            unsigned number,keys,shift;require_view(bool(epoch_plan>>number>>keys>>shift)&&number==frame&&keys<=65535&&shift==0,"epoch Stage2 input/order/width");
            if(wait_inputs) {
                for(unsigned attempt=0;;++attempt) {
                    require_view(attempt<10000 && scene.live_main() && !scene.pause_active(),"epoch unconfigured blocking owner");
                    const bool blocked=scene.dialog_active();const auto status=scene.dialog_status();
                    const auto* go=scene.main_state().game_over();const int go_before=go ? int(go->phase()) : -1;
                    auto held=blocked ? std::uint16_t((status==th04::portable::dialog::Status::press ||
                        status==th04::portable::dialog::Status::running) ? 0x1000 : 0) : translate(keys);
                    if(go) {
                        const bool waiting=go->phase()==gameover::Phase::press || go->phase()==gameover::Phase::menu;
                        held=std::uint16_t(waiting && attempt%20<10 ? 0x1000 : 0);
                    }
                    scene.advance(held,false,false);
                    if(blocked || scene.dialog_active() || go || scene.main_state().game_over()) {
                        const std::string kind=go || scene.main_state().game_over() ? "continue" : "dialogue";
                        const auto cue=std::make_pair(frame,kind);
                        wait_blocks<<frame<<' '<<attempt<<' '<<kind<<' '<<unsigned(status)<<' '<<go_before<<' '
                            <<held<<' '<<scene.main_state().frames()<<' '<<scene.dialog_offset()<<' '
                            <<scene.main_state().player_input()<<' '<<scene.main_state().consumed_input()<<' '
                            <<scene.process_random_draws()-base_draws<<' '
                            <<ring_offset+scene.main_state().random_samples()-base_samples<<'\n';
                        require_view(std::find(wait_frames.begin(),wait_frames.end(),cue)!=wait_frames.end(),"epoch undeclared wait cue");
                        if(observed_wait_frames.empty() || observed_wait_frames.back()!=cue)observed_wait_frames.push_back(cue);
                    }
                    if(scene.main_state().frames()==frame+1)break;
                    require_view(scene.main_state().frames()==frame && (scene.dialog_active() ||
                        scene.main_state().game_over()),"epoch non-UI stalled frame");
                }
            } else scene.advance(translate(keys),false,false);
            require_view(scene.main_state().frames()==frame+1&&scene.resident().resource_stage==1&&!scene.dialog_active()&&!scene.main_state().game_over(),"epoch unexpected owner or incomplete Stage2 update");
            observe("stage2-score",scene.main_state());
            completed=frame+1;
            if(until_clear && scene.main_state().next_stage_requested())break;
        }
        if(until_clear) {
            require_view(completed>0 && completed<=extent && scene.main_state().next_stage_requested() &&
                scene.resident().resource_stage==1 && scene.resident().stage==2,"epoch Stage2 clear not observed");
            observe("stage2-return",scene.main_state());
            // A bounded input schedule can extend past the actual clear. Check
            // every declared unused row without pretending it was consumed.
            for(unsigned frame=completed;frame<extent;++frame) {
                unsigned number,keys,shift;
                require_view(bool(epoch_plan>>number>>keys>>shift) && number==frame && keys<=65535 && shift==0,
                    "epoch unused Stage2 input/order/width");
            }
            ring_offset+=scene.main_state().random_samples();
            for(unsigned frame=0;frame<stage3_updates;++frame) {
                unsigned keys=stage3_keys;
                if(extended_stage3) {
                    unsigned number,shift;
                    require_view(bool(clear_plan>>number>>keys>>shift) && number==frame && keys<=65535 && shift==0,
                        "epoch Stage3 input/order/width");
                    require_view(frame!=0 || keys==stage3_keys,"epoch Stage3 initial input disagreement");
                }
                for(unsigned attempt=0;;++attempt) {
                    require_view(attempt<10000 && scene.live_main() && !scene.pause_active(),"epoch Stage3 unconfigured blocking owner");
                    const bool blocked=scene.dialog_active();const auto status=scene.dialog_status();
                    const auto* go=scene.main_state().game_over();const int go_before=go ? int(go->phase()) : -1;
                    auto held=blocked ? std::uint16_t((status==th04::portable::dialog::Status::press ||
                        status==th04::portable::dialog::Status::running) ? 0x1000 : 0) : translate(keys);
                    if(go) {
                        const bool waiting=go->phase()==gameover::Phase::press || go->phase()==gameover::Phase::menu;
                        held=std::uint16_t(waiting && attempt%20<10 ? 0x1000 : 0);
                    }
                    scene.advance(held,false,false);
                    require_view(scene.live_main(),("epoch Stage3 MAIN departed at frame "+std::to_string(frame)).c_str());
                    if(blocked || scene.dialog_active() || go || scene.main_state().game_over()) {
                        const std::string kind=go || scene.main_state().game_over() ? "continue" : "dialogue";
                        const auto cue=std::make_pair(frame,kind);
                        stage3_blocks<<frame<<' '<<attempt<<' '<<kind<<' '<<unsigned(status)<<' '<<go_before<<' '
                            <<held<<' '<<scene.main_state().frames()<<' '<<scene.dialog_offset()<<' '
                            <<scene.main_state().player_input()<<' '<<scene.main_state().consumed_input()<<' '
                            <<scene.process_random_draws()-base_draws<<' '
                            <<ring_offset+scene.main_state().random_samples()-base_samples<<'\n';
                        require_view(extended_stage3 && std::find(stage3_wait_frames.begin(),stage3_wait_frames.end(),cue)!=stage3_wait_frames.end(),
                            ("epoch undeclared Stage3 wait "+std::to_string(frame)+" "+kind).c_str());
                        if(stage3_observed_wait_frames.empty() || stage3_observed_wait_frames.back()!=cue)
                            stage3_observed_wait_frames.push_back(cue);
                    }
                    if(scene.main_state().frames()==frame+1)break;
                    require_view(scene.main_state().frames()==frame && (scene.dialog_active() ||
                        scene.main_state().game_over()),"epoch Stage3 non-UI stalled frame");
                }
                require_view(scene.resident().resource_stage==2 && scene.main_state().frames()==frame+1 &&
                    !scene.dialog_active() && !scene.main_state().game_over(),"epoch incomplete Stage3 update");
                observe("stage3-score",scene.main_state());
                require_view(!scene.main_state().next_stage_requested(),"epoch Stage3 departed before budget");
            }
            if(extended_stage3) {
                clear_plan>>std::ws;require_view(clear_plan.peek()==std::char_traits<char>::eof(),"epoch trailing Stage3 inputs");
                require_view(stage3_observed_wait_frames==stage3_wait_frames,"epoch configured Stage3 wait not observed");
            }
            std::ofstream summary(output/"stage-clear.json");
            summary<<"{\"complete\":true,\"stage2_update_budget\":"<<extent
                <<",\"stage2_complete_updates\":"<<completed<<",\"unused_stage2_inputs\":"<<(extent-completed)
                <<",\"stage3_complete_updates\":"<<scene.main_state().frames()<<"}\n";
            require_view(bool(summary),"epoch clear summary unavailable");
        }
        epoch_plan>>std::ws;require_view(epoch_plan.peek()==std::char_traits<char>::eof(),"epoch trailing input");
        require_view(observed_wait_frames==wait_frames,"epoch configured wait not observed");
    }

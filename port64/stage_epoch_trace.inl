// Optional stage-boundary diagnostic. Inputs advance the normal scene;
// observations never assign gameplay state, random values or clock phase.
    if(fs::exists(fs::path(assets.save_directory)/"stage-epoch-plan.txt")) {
        require_view(updates==9835,"epoch fixture requires the attested preceding component extent");
        std::ifstream epoch_plan(fs::path(assets.save_directory)/"stage-epoch-plan.txt");
        std::string magic;unsigned version,extent,final_keys,final_shift;
        require_view(bool(epoch_plan>>magic>>version>>extent>>final_keys>>final_shift) &&
            magic=="TH04_STAGE_EPOCH" && version==1 && extent>0 && extent<=3996 && final_keys<=65535 && final_shift==0,"epoch fixture header/input");
        std::ofstream epoch(output/"stage-native.jsonl"),epoch_pools(output/"stage2-pools.bin",std::ios::binary),tail_pools(output/"stage1-tail-pools.bin",std::ios::binary);
        require_view(bool(epoch)&&bool(epoch_pools)&&bool(tail_pools),"epoch output unavailable");
        epoch_pools.write("TH04OP1\n",8);tail_pools.write("TH04OP1\n",8);
        const stage::Program stage2_program(assets.stage2.standard);
        std::uint64_t ring_offset=0;unsigned ordinal=0;
        const auto observe=[&](const char* label,const gameplay::State& s) {
            const auto dump=[&](const auto& bytes){constexpr char digits[]="0123456789abcdef";for(auto v:bytes)epoch<<digits[unsigned(v)>>4]<<digits[unsigned(v)&15];};
            bool comma=false;
            const auto field=[&](const char* name,const auto& bytes) {if(comma)epoch<<',';comma=true;epoch<<'"'<<name<<"\":\"";dump(bytes);epoch<<'"';};
            const auto integer=[&](const char* name,std::uint64_t value,unsigned size) {std::vector<std::uint8_t> b;for(unsigned i=0;i<size;++i)b.push_back(std::uint8_t(value>>(i*8)));field(name,b);};
            const auto& life=s.life();const auto& board=s.scoreboard();const auto& resident=scene.resident();
            epoch<<"{\"ordinal\":"<<ordinal++<<",\"label\":\""<<label<<"\",\"resource_stage\":"<<+resident.resource_stage<<",\"resident_stage\":"<<+resident.stage<<",\"fields\":{";
            integer("frame",s.frames(),2);integer("stage",resident.resource_stage,1);integer("input",s.consumed_input(),2);
            field("score_digits",board.digits);integer("score_delta",s.score().score_delta,4);integer("score_delta_frame",board.frame_delta,4);integer("lcg",scene.process_random_state(),4);field("ring",s.random_ring_bytes());integer("ring_cursor",s.random_cursor(),2);
            th04::portable::demo_wire::Writer position;position.point(s.player().position().current);field("player_pos",position.data);
            integer("power",s.score().power,1);integer("hit",life.hit,1);integer("invincibility",life.invincibility,1);integer("respawn",life.respawn_time,1);
            const auto& boss=s.boss_snapshot();th04::portable::demo_wire::Writer owner;owner.movement(boss.position);owner.word(boss.hp);owner.byte(boss.sprite);owner.byte(boss.phase);owner.word(boss.phase_frame);owner.byte(boss.damage);owner.byte(boss.mode);owner.byte(boss.angle);owner.byte(boss.patterns_or_bonus);owner.word(boss.end_hp);field("boss",owner.data);field("boss_statebyte",boss.additional);th04::portable::demo_wire::Writer hitbox;hitbox.point(boss.hitbox_radius);field("boss_hitbox_radius",hitbox.data);integer("boss_phase_timed_out",boss.timed_out,1);
            const auto target=s.homing_target().value_or(th04::portable::motion::Point{-15984,-15984});th04::portable::demo_wire::Writer homing;homing.point(target);field("homing",homing.data);
            epoch<<"},\"lives\":"<<+s.score().remaining_lives<<",\"bombs\":"<<+s.score().remaining_bombs<<",\"misses\":"<<+resident.miss_count<<",\"bombs_used\":"<<+resident.bombs_used<<",\"lcg_calls\":"<<scene.process_random_draws()-base_draws<<",\"ring_samples_since_fill\":"<<s.random_samples()<<",\"ring_calls\":"<<ring_offset+s.random_samples()-base_samples<<"}\n";
        };
        const auto translate=[](unsigned keys) {return std::uint16_t((keys&0x2fu)|(keys&0x10u?0x800u:0)|(keys&0x1000u?0x2000u:0)|(keys&0x2000u?0x1000u:0));};
        scene.main_state().set_actor_observer([&](const gameplay::State& s) {
            if(scene.resident().resource_stage==0) {th04::portable::demo_wire::pools(tail_pools,0,s,program);observe("stage1-actor",s);}
            else {th04::portable::demo_wire::pools(epoch_pools,0,s,stage2_program);observe("stage2-actor",s);}
        });
        unsigned guard=0;
        while(!scene.main_state().next_stage_requested()) {
            require_view(++guard<=16 && scene.live_main() && !scene.dialog_active(),"epoch departure did not complete naturally");
            scene.advance(translate(final_keys),false,false);observe("stage1-score",scene.main_state());
        }
        observe("stage1-return",scene.main_state());ring_offset=scene.main_state().random_samples();
        scene.set_stage_init_observer([&](const gameplay::State& s) {
            require_view(s.frames()==0 && scene.resident().resource_stage==1,"epoch initialization boundary");
            th04::portable::demo_wire::pools(epoch_pools,0,s,stage2_program);observe("init_return",s);
        });
        for(unsigned frame=0;frame<extent;++frame) {
            unsigned number,keys,shift;require_view(bool(epoch_plan>>number>>keys>>shift)&&number==frame&&keys<=65535&&shift==0,"epoch Stage2 input/order/width");
            scene.advance(translate(keys),false,false);
            require_view(scene.main_state().frames()==frame+1&&scene.resident().resource_stage==1&&!scene.dialog_active()&&!scene.main_state().game_over(),"epoch unexpected owner or incomplete Stage2 update");
            observe("stage2-score",scene.main_state());
        }
        epoch_plan>>std::ws;require_view(epoch_plan.peek()==std::char_traits<char>::eof(),"epoch trailing input");
    }

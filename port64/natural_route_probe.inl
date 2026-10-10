// Maintained headless route control: ordinary FrontEnd, key inputs only.
// No target/game-state writes or actor-control hit suppression.
void run_natural_route_checks(const PiImage& background,const CdgSheet& numerals,
    const CdgSheet& labels,const CdgSheet& cursors,const PiImage& selection_background,
    const CdgSheet& portraits,const MainAssets& assets,const std::string& output) {
    namespace fs=std::filesystem;
    unsigned rank=0,character=0,limit=150000,render_every=0,continues_allowed=0,extra=0,shot_type=0,pilot=0;
    std::ifstream plan(fs::path(assets.save_directory)/"route-plan.txt");
    require_view(bool(plan>>rank>>character>>limit>>render_every>>continues_allowed>>extra),"six-field route plan required");
    plan>>std::ws;
    if(plan.peek()!=std::char_traits<char>::eof()) {
        require_view(bool(plan>>shot_type),"invalid optional shot type");plan>>std::ws;
        if(plan.peek()!=std::char_traits<char>::eof()) {
            require_view(bool(plan>>pilot),"invalid optional pilot");plan>>std::ws;
        }
    }
    require_view(plan.peek()==std::char_traits<char>::eof() && extra<=1 && rank<4 && character<2 &&
                 shot_type<2 && pilot<=1 && render_every<=1 && limit>0 && limit<=500000 && assets.muted,"invalid route plan/mute");
    const fs::path out(output);require_view(!fs::exists(out),"fresh route output required");fs::create_directories(out);
    std::ofstream inputs(out/"inputs.txt",std::ios::binary),trace(out/"state.txt",std::ios::binary);
    std::ofstream startup_inputs(out/"startup-inputs.txt",std::ios::binary),menu_inputs(out/"menu-inputs.txt",std::ios::binary);
    th04::portable::configuration::HostStore config(assets.save_directory);
    if(config.setup_required()) {
        config.complete_setup(2,1);auto options=config.options();options.rank=std::uint8_t(rank);
        options.lives=6;options.bombs=2;options.turbo=true;config.save(options,false);
    }
    FrontEnd scene(background,numerals,labels,cursors,selection_background,portraits,&assets,gameplay::Mode::ordinary);
    scene.enable_configuration();scene.enable_registration();
    unsigned ticks=0;while(scene.startup_scene() && ticks<3000) {
        startup_inputs<<ticks++<<" 0 0\n";scene.advance(0,false,render_every!=0);
    }
    require_view(ticks<3000 && !scene.setup_scene(),"natural route startup failed");
    scene.repaint();write_bmp((out/"startup-menu.bmp").string(),scene.frame());
    const auto press=[&](menu::Input key){menu_inputs<<unsigned(key)<<'\n';scene.input(key);};
    if(extra){require_view(scene.menu_state().extra_unlocked(),"Extra requires a physically earned normal clear");press(menu::Input::down);}
    press(menu::Input::confirm);if(character)press(menu::Input::right);
    press(menu::Input::confirm);if(shot_type)press(menu::Input::down);press(menu::Input::confirm);
    require_view(scene.live_main() && scene.main_state().mode()==gameplay::Mode::ordinary,"ordinary MAIN entry required");
    require_view(unsigned(scene.resident().playchar)==character && unsigned(scene.resident().shot_type)==shot_type,
                 "route entered a different character or shot");
    unsigned last_stage=99,last_generation=99,last_go=0,continue_visits=0,ending_visits=0,registration_visits=0,extra_visits=0;
    bool was_go=false,was_ending=false,was_registration=false,was_extra=false,fresh_op=false;
    for(ticks=0;ticks<limit;++ticks) {
        std::uint16_t keys=0;bool shift=false;double danger=1e20;
        if(scene.live_main()) {
            const auto& s=scene.main_state();const auto& p=s.player().position();
            const auto* go=s.game_over();
            if(go) {
                if(!was_go){++continue_visits;last_go=ticks;}was_go=true;
                keys=(ticks-last_go)%20<10 ? (continue_visits<=continues_allowed ? shot::input_shot : 0x2000) : 0;
            } else if(pilot==1) {
                // A stationary held shot exercises ordinary hits and death
                // without writing any player, actor or life state. Dialog
                // ownership still receives released/pressed shot keys.
                was_go=false;
                keys=scene.dialog_status()==dialog::Status::idle || ticks%20<10 ? shot::input_shot : 0;
            } else {
                was_go=false;
                double target_x=192*16,target_y=304*16;
                if(s.boss_active())target_x=s.boss_snapshot().position.current.x;
                else {
                    double distance=1e20;
                    for(const auto& item:s.items().entities())if(item.flag==th04::portable::item::Flag::alive) {
                        const auto q=item.position.current;
                        if(q.y<16*220 || q.y>16*345)continue;
                        const double dx=q.x-p.current.x,dy=q.y-p.current.y;
                        const double d=dx*dx+dy*dy;
                        if(d<distance){distance=d;target_x=q.x;target_y=std::max<int>(q.y,16*240);}
                    }
                }
                double best=1e30;unsigned chosen=0;bool focused=false;
                for(unsigned focus=0;focus<2;++focus)for(unsigned move=0;move<9;++move) {
                    const int dx=int(move%3)-1,dy=int(move/3)-1;
                    const double speed=(dx && dy ? 48.0 : 64.0)/(focus ? 2 : 1);
                    double risk=0,minimum=1e20;
                    for(unsigned f=1;f<=12;++f) {
                        const double x=std::clamp(p.current.x+dx*speed*f,128.0,6016.0);
                        const double y=std::clamp(p.current.y+dy*speed*f,128.0,5632.0);
                        for(const auto& b:s.bullets().snapshot().entities) {
                            if(!b.flag || unsigned(b.phase)>=3)continue;
                            const double bx=b.position.current.x+double(b.position.velocity.x)*f;
                            const double by=b.position.current.y+double(b.position.velocity.y)*f;
                            const double ax=bx-x,ay=by-y,d=ax*ax+ay*ay;
                            minimum=std::min(minimum,d);
                            if(d<256.0*256)risk+=1000000.0/(1+d)*(13-f);
                        }
                        for(const auto& e:s.enemies().snapshot().entities) {
                            if(!e.flag || !e.player_collision)continue;
                            const double ex=e.position.current.x+double(e.position.velocity.x)*f;
                            const double ey=e.position.current.y+double(e.position.velocity.y)*f;
                            const double ax=ex-x,ay=ey-y,d=ax*ax+ay*ay;
                            minimum=std::min(minimum,d);
                            if(std::abs(ax)<512 && std::abs(ay)<512)risk+=2000000.0/(1+d)*(13-f);
                        }
                        const double tx=(x-target_x)/16,ty=(y-target_y)/16;
                        risk+=(tx*tx+ty*ty)*0.002;
                    }
                    if(risk<best){best=risk;chosen=move;focused=focus;danger=minimum;}
                }
                const int dx=int(chosen%3)-1,dy=int(chosen/3)-1;
                keys=shot::input_shot|std::uint16_t(dx<0 ? player::left : dx>0 ? player::right : 0)|
                    std::uint16_t(dy<0 ? player::up : dy>0 ? player::down : 0);shift=focused;
                if(danger<256.0*256 && !s.life().invincibility && !s.life().bombing && s.score().remaining_bombs)keys|=0x800;
                // Dialogues require release/press gates, so the same recorded
                // shot key pulses during their ordinary blocking ownership.
                if(scene.dialog_status()!=dialog::Status::idle)keys=(ticks%20<10 ? shot::input_shot : 0);
            }
            trace<<ticks<<' '<<scene.generation()<<' '<<unsigned(scene.resident().stage)<<' '<<s.frames()<<' '
                <<p.current.x<<' '<<p.current.y<<' '<<unsigned(s.score().remaining_lives)<<' '
                <<unsigned(s.score().remaining_bombs)<<' '<<unsigned(s.score().power)<<' '
                <<unsigned(s.life().misses)<<' '<<unsigned(s.life().bombs_used)<<' '
                <<unsigned(s.life().invincibility)<<' '<<unsigned(s.life().respawn_time)<<' '
                <<unsigned(s.boss_active())<<' '<<(s.boss_active() ? unsigned(s.boss_snapshot().phase) : 0)<<' '
                <<(s.boss_active() ? s.boss_snapshot().hp : 0)<<' '<<unsigned(bool(go))<<' '
                <<s.awarded_score_units()<<' '<<unsigned(scene.dialog_status())<<'\n';
            if(scene.resident().stage!=last_stage || scene.generation()!=last_generation) {
                scene.repaint();write_bmp((out/("stage-"+std::to_string(scene.resident().stage)+"-generation-"+std::to_string(scene.generation())+".bmp")).string(),scene.frame());
                last_stage=scene.resident().stage;last_generation=scene.generation();
            }
        } else {
            if(scene.ending() && !was_ending){++ending_visits;std::ofstream name(out/"ending-name.txt",std::ios::binary);name<<scene.ending()->script_name()<<'\n';}
            if(scene.extra_route() && !was_extra)++extra_visits;
            was_extra=bool(scene.extra_route());
            if(scene.registration_scene() && !was_registration)++registration_visits;
            was_ending=bool(scene.ending());was_registration=bool(scene.registration_scene());
            keys=ticks%20<10 ? (scene.registration_scene() ? 0x2000 : shot::input_shot) : 0;
            trace<<ticks<<' '<<scene.generation()<<' '<<unsigned(scene.program())<<" CHILD "<<unsigned(was_ending)<<' '<<unsigned(was_registration)<<'\n';
            if(scene.program()==application::Program::op && scene.generation()>2 && !scene.startup_scene()) {
                fresh_op=true;scene.repaint();write_bmp((out/"fresh-op.bmp").string(),scene.frame());break;
            }
        }
        inputs<<ticks<<' '<<keys<<' '<<unsigned(shift)<<'\n';
        scene.advance(keys,shift,render_every!=0);
        if(ticks%4096==0)std::cout<<"NATURAL exploration tick "<<ticks<<" stage "<<unsigned(scene.resident().stage)<<" generation "<<scene.generation()<<std::endl;
    }
    std::ofstream result(out/"result.txt",std::ios::binary);result<<"ticks "<<ticks<<" fresh_op "<<fresh_op<<" gameover_visits "<<continue_visits<<" ending_visits "<<ending_visits<<" registration_visits "<<registration_visits<<" extra_visits "<<extra_visits<<" render_every "<<render_every<<'\n';
    std::cout<<"NATURAL exploration finished tick "<<ticks<<" fresh OP "<<fresh_op<<" ending "<<ending_visits<<std::endl;
}

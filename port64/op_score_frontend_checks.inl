// Physical saved-score startup/restart and registration-close integration.
// The registration run is an explicit child-scene fixture, not survival.
void run_op_score_checks(const PiImage& background,const CdgSheet& numerals,
    const CdgSheet& labels,const CdgSheet& cursors,const PiImage& selection_background,
    const CdgSheet& portraits,const MainAssets& assets,const std::string& destination) {
    namespace fs=std::filesystem;
    const fs::path directory(destination),inputs(assets.save_directory);
    require_view(!fs::exists(directory) && assets.muted,"OP score checks require fresh muted outputs");
    fs::create_directories(directory);
    std::ifstream cases(inputs/"cases.txt");require_view(bool(cases),"original OP score fixtures missing");
    const auto hex=[](std::ostream& out,const auto& bytes) {
        const char* digits="0123456789abcdef";
        for(auto value:bytes)out<<digits[unsigned(value)>>4]<<digits[unsigned(value)&15];
    };
    const auto report=[&](FrontEnd& scene,const fs::path& location) {
        std::ofstream out(location/"read.txt",std::ios::binary);const auto& s=scene.op_scores().snapshot();
        out<<scene.process_random_state()<<' '<<+s.rank<<' '<<+s.extra_unlocked<<' ';
        for(const auto& row:s.cleared)hex(out,row);
        out<<' ';hex(out,s.first);out<<' ';hex(out,s.second);
        out<<' ';for(const auto& row:scene.op_scores().availability(true))for(bool b:row)out<<int(b);
        out<<'\n';require_view(bool(out),"OP read report failed");
        const auto seed=scene.process_random_state();scene.repaint();const auto pixels=scene.frame().pixels;scene.repaint();
        require_view(scene.frame().pixels==pixels && scene.process_random_state()==seed,"OP repaint consumed RNG");
        write_bmp((location/"op.bmp").string(),scene.frame());
    };
    const auto launch=[&](FrontEnd& scene,bool extra,const fs::path& location) {
        if(extra)scene.input(menu::Input::down);
        scene.input(menu::Input::confirm);scene.input(menu::Input::confirm);scene.input(menu::Input::confirm);
        require_view(scene.live_main() && scene.main_resources_alive(),"saved OP selection failed MAIN entry");
        require_view(scene.resident().stage==(extra ? 6 : 0) && (!extra || scene.extra_resources_valid()),"saved OP chose wrong stage/resources");
        std::ofstream out(location/"selection.txt",std::ios::binary);
        out<<unsigned(scene.resident().playchar)<<' '<<unsigned(scene.resident().shot_type)<<' '<<unsigned(scene.resident().stage)<<'\n';
        require_view(bool(out),"OP selection report failed");
    };
    std::string name;unsigned count=0;
    while(cases>>name) {
        require_view(name.find('/')==std::string::npos && name.find("..") ==std::string::npos,"invalid OP fixture name");
        const auto location=directory/name;fs::create_directories(location/"save");auto input=assets;
        input.save_directory=(location/"save").string();
        if(fs::exists(inputs/(name+".SCR")))fs::copy_file(inputs/(name+".SCR"),location/"save"/"GENSOU.SCR");
        FrontEnd scene(background,numerals,labels,cursors,selection_background,portraits,&input);
        scene.enable_registration();report(scene,location);
        const bool extra=scene.op_scores().extra_unlocked();launch(scene,extra,location);
        fs::create_directories(location/"restart");
        FrontEnd restarted(background,numerals,labels,cursors,selection_background,portraits,&input);
        restarted.enable_registration();report(restarted,location/"restart");
        // Ordinary selection ignores the Extra mask, including an empty mask.
        launch(restarted,false,location/"restart");
        std::cout<<"OP_SCORE "<<name<<" extra="<<extra<<" physical_restart=1 muted=1\n";++count;
    }
    require_view(count>0 && cases.eof(),"OP fixture index malformed");
    for(unsigned character=0;character<2;++character)for(unsigned rank=1;rank<4;++rank) {
        const auto name="registration-c"+std::to_string(character)+"-r"+std::to_string(rank);
        const auto location=directory/name;fs::create_directories(location/"save");auto input=assets;
        input.save_directory=(location/"save").string();fs::copy_file(inputs/"zero.SCR",location/"save"/"GENSOU.SCR");
        FrontEnd scene(background,numerals,labels,cursors,selection_background,portraits,&input);
        scene.enable_registration();require_view(!scene.op_scores().extra_unlocked(),"baseline is already unlocked");
        scene.seed_registration_fixture(character,rank,0);const auto generation=scene.generation();
        for(unsigned i=0;i<35;++i)scene.advance(0,false,false);
        require_view(scene.registration_scene()->status()==registration::Status::editing,"registration clear fixture did not enter editing");
        const auto press=[&](std::uint16_t held){scene.advance(0,false,false);scene.advance(0,false,false);scene.advance(held,false,false);};
        press(shot::input_shot);press(0x2000);
        require_view(scene.registration_scene()->status()==registration::Status::fade_out && !scene.op_scores().extra_unlocked(),"OP read ran before registration blackout");
        for(unsigned i=0;i<17;++i) {scene.advance(0,false,false);require_view(scene.program()==application::Program::maine,"OP entered before full blackout");}
        scene.advance(0,false,false);
        require_view(scene.program()==application::Program::op && scene.generation()==generation+1 && scene.process_random_state()==1 &&
            !scene.registration_scene() && !scene.main_resources_alive(),"registration failed fresh OP release/read");
        const auto& flags=scene.op_scores().snapshot().cleared;
        for(unsigned c=0;c<2;++c)for(unsigned r=0;r<5;++r)
            require_view(flags[c][r]==((c==character && r==rank) ? (1u<<character) : 0),"fresh OP did not read exactly the saved clear bit");
        require_view(scene.op_scores().extra_unlocked(),"saved clear did not unlock fresh OP");report(scene,location);
        launch(scene,true,location);
        require_view(unsigned(scene.resident().playchar)==character && unsigned(scene.resident().shot_type)==character,"locked combination remained selectable");
        FrontEnd restarted(background,numerals,labels,cursors,selection_background,portraits,&input);
        restarted.enable_registration();fs::create_directories(location/"restart");report(restarted,location/"restart");launch(restarted,true,location/"restart");
        std::cout<<"OP_SCORE_REGISTRATION "<<name<<" writer_close=1 fresh_op=1 extra_main=1 physical_restart=1 muted=1\n";
    }
}

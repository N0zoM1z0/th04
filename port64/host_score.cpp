#include "host_score.hpp"
#include <algorithm>
#include <chrono>
#include <cstdlib>
#include <fstream>
#include <stdexcept>
#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#endif

namespace th04::portable::score_file {
namespace fs=std::filesystem;
namespace {
void require(bool b,const char* message) {if(!b)throw std::runtime_error(message);}
}
fs::path HostStore::default_directory() {
#ifdef _WIN32
    if(const auto* local=std::getenv("LOCALAPPDATA"))
        if(*local)return fs::path(local)/"TH04";
    if(const auto* profile=std::getenv("USERPROFILE"))
        if(*profile)return fs::path(profile)/"AppData"/"Local"/"TH04";
#else
    if(const auto* state=std::getenv("XDG_DATA_HOME"))
        if(*state && fs::path(state).is_absolute())return fs::path(state)/"th04";
    if(const auto* home=std::getenv("HOME"))
        if(*home)return fs::path(home)/".local"/"share"/"th04";
#endif
    throw std::runtime_error("cannot determine native save directory; supply --save-dir");
}
HostStore::HostStore(fs::path directory):path_(std::move(directory)/"GENSOU.SCR") {
    const bool present=fs::exists(path_);
    if(present) {
        std::ifstream input(path_,std::ios::binary);
        require(bool(input),"cannot read native score file");
        pending_={std::istreambuf_iterator<char>(input),{}};
        require(!input.bad(),"native score read failed");
    }
    // Original unchecked short reads can leave all-zero HI bytes whose
    // eight-bit checksum passes, then index an undefined numeral pattern.
    // At the HOST boundary reject an incomplete ten-section file as missing.
    // Keep File's independently controlled short-read semantics unchanged.
    file_=File(present && pending_.size()>=section_count*section_size,pending_);
}
void HostStore::apply(const Operation& op) {
    switch(op.kind) {
    case IO::exists:break;
    case IO::open:
        require(!opened_,"native score file already open");
        mode_=OpenMode(op.a);opened_=true;dirty_=false;
        if(mode_==OpenMode::create) {pending_.clear();dirty_=true;}
        position_=mode_==OpenMode::append ? pending_.size() : 0;break;
    case IO::seek:
        require(opened_ && (op.b==0 || op.b==1),"invalid native score seek");
        position_=(op.b ? position_ : 0)+std::uint32_t(op.a);break;
    case IO::read:
        require(opened_ && op.b>=0,"invalid native score read");
        position_+=unsigned(op.b);break;
    case IO::write:
        require(opened_ && mode_!=OpenMode::read && op.b>=0 &&
                unsigned(op.b)==op.data.size(),"invalid native score write");
        if(pending_.size()<position_+op.data.size())pending_.resize(position_+op.data.size());
        std::copy(op.data.begin(),op.data.end(),pending_.begin()+position_);
        position_+=op.data.size();dirty_=true;break;
    case IO::close:
        require(opened_,"native score file already closed");
        if(dirty_)commit();
        opened_=false;dirty_=false;break;
    }
}
Byte HostStore::save_continue(Byte character,Byte rank,Byte stage,bool turbo,
                              const score::Digits& digits,const Random& random) {
    const auto start=file_.operations().size();
    Section section{};
    const auto place=continue_main(section,file_,character,rank,stage,turbo,digits,random);
    for(auto at=start;at<file_.operations().size();++at)apply(file_.operations()[at]);
    return place;
}
score::Digits HostStore::read_main_highscore(Byte character,Byte rank,const Random& random) {
    const auto start=file_.operations().size();Section section{};
    const auto highscore=load_hiscore_main(section,file_,character,rank,random);
    for(auto at=start;at<file_.operations().size();++at)apply(file_.operations()[at]);
    return highscore;
}
void HostStore::commit() {
    fs::create_directories(path_.parent_path());
    // create_directory reserves our temporary namespace atomically. Never
    // truncate a previous score file or a pre-existing temporary file.
    const auto stamp=std::chrono::steady_clock::now().time_since_epoch().count();
    fs::path temporary;
    for(unsigned attempt=0;attempt<100;++attempt) {
        auto candidate=path_.parent_path()/(".score-pending-"+std::to_string(stamp)+"-"+std::to_string(attempt));
        if(fs::create_directory(candidate)) {temporary=std::move(candidate);break;}
    }
    require(!temporary.empty(),"cannot reserve native score temporary directory");
    const auto data=temporary/"score";
    try {
        std::ofstream output(data,std::ios::binary);
        require(bool(output),"cannot create native score temporary file");
        output.write(reinterpret_cast<const char*>(pending_.data()),std::streamsize(pending_.size()));
        output.flush();require(bool(output),"cannot write native score temporary file");
        output.close();require(bool(output),"cannot close native score temporary file");
#ifdef _WIN32
        if(!MoveFileExW(data.c_str(),path_.c_str(),MOVEFILE_REPLACE_EXISTING|MOVEFILE_WRITE_THROUGH))
            throw std::runtime_error("cannot replace native score file (Win32 error "+
                                     std::to_string(GetLastError())+")");
#else
        fs::rename(data,path_);
#endif
        fs::remove(temporary);++commits_;
    } catch(...) {
        std::error_code ignored;fs::remove(data,ignored);fs::remove(temporary,ignored);throw;
    }
}
} // namespace th04::portable::score_file

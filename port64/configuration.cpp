#include "configuration.hpp"
#include <algorithm>
#include <chrono>
#include <fstream>
#include <stdexcept>
#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#ifndef NOMINMAX
#define NOMINMAX
#endif
#include <windows.h>
#endif

namespace th04::portable::configuration {
namespace fs=std::filesystem;
namespace {
void require(bool ok,const char* message) {if(!ok)throw std::runtime_error(message);}
Options first(const Bytes& bytes) {
    require(bytes.size()>=10,"incomplete TH04 configuration record");
    Options options{};std::copy_n(bytes.begin(),6,options.begin());return options;
}
}
std::uint8_t checksum(const Options& options) {
    unsigned sum=0;for(auto v:options)sum+=v;return std::uint8_t(sum);
}
Result load(const Bytes& bytes) {
    Result result;result.file=bytes;result.options=first(bytes);
    result.operations={{IO::open,0},{IO::read,10,10,Bytes(bytes.begin(),bytes.begin()+10)},{IO::close}};
    auto& o=result.options;
    if(o[1]>6 || !o[1])o[1]=3;
    if(o[2]>2)o[2]=2;
    if(o[3]>=3)o[3]=0;
    if(o[4]>=3)o[4]=0;
    return result;
}
Result save(const Bytes& bytes,const Options& options,bool exiting) {
    Result result;result.file=bytes;result.options=options;
    result.operations={{IO::open,1},{IO::seek,0}};
    if(result.file.size()<10)result.file.resize(10);
    std::copy(options.begin(),options.end(),result.file.begin());
    if(exiting) {
        std::fill(result.file.begin()+6,result.file.begin()+9,0);
        result.file[9]=checksum(options);
        result.operations.push_back({IO::write,10,10,Bytes(result.file.begin(),result.file.begin()+10)});
    } else {
        result.operations.push_back({IO::write,6,6,Bytes(options.begin(),options.end())});
        result.operations.push_back({IO::seek,9});
        result.file[9]=checksum(options);
        result.operations.push_back({IO::write,1,1,Bytes{result.file[9]}});
    }
    result.operations.push_back({IO::close});return result;
}
Options encode(const menu::Options& o) {return {o.rank,o.lives,o.bombs,o.bgm_mode,o.se_mode,std::uint8_t(o.turbo)};}
menu::Options decode(const Options& o) {
    return {o[0],o[1],o[2],o[3],o[4],o[5]!=0};
}
HostStore::HostStore(fs::path directory):path_(std::move(directory)/"MIKO.CFG") {
    if(fs::exists(path_)) {
        std::ifstream input(path_,std::ios::binary);require(bool(input),"cannot read native configuration");
        bytes_={std::istreambuf_iterator<char>(input),{}};require(!input.bad(),"native configuration read failed");
    }
    // Host repair defines the missing-file checksum and rejects unsafe typed
    // values. RankFF retains the original request for OP's first setup scene.
    bool valid=bytes_.size()>=10;
    if(valid) {const auto o=first(bytes_);valid=checksum(o)==bytes_[9] && (o[0]<4 || o[0]==255) && o[5]<2;}
    if(!valid) {
        const auto replacement=configuration::save({},Options{255,3,2,1,1,1},true).file;
        commit(replacement);bytes_=replacement;repaired_=true;
    }
    auto raw=configuration::load(bytes_).options;setup_required_=raw[0]==255;
    // A typed menu cannot index rankFF. The pending scene owns it until both
    // selections finish; ordinary menu/MAIN input is blocked by that owner.
    if(setup_required_)raw[0]=1;
    options_=decode(raw);
}
void HostStore::complete_setup(std::uint8_t bgm,std::uint8_t se) {
    require(setup_required_ && bgm<3 && se<3,"invalid native setup completion");
    options_.rank=1;options_.bgm_mode=bgm;options_.se_mode=se;setup_required_=false;
}
void HostStore::save(const menu::Options& options,bool exiting) {
    auto raw=encode(options);if(setup_required_)raw[0]=255;
    const auto next=configuration::save(bytes_,raw,exiting);
    commit(next.file);bytes_=next.file;options_=options;
}
void HostStore::commit(const Bytes& bytes) {
    fs::create_directories(path_.parent_path());
    fs::path temporary;const auto stamp=std::chrono::steady_clock::now().time_since_epoch().count();
    for(unsigned attempt=0;attempt<100;++attempt) {
        auto p=path_.parent_path()/(".config-pending-"+std::to_string(stamp)+"-"+std::to_string(attempt));
        if(fs::create_directory(p)) {temporary=std::move(p);break;}
    }
    require(!temporary.empty(),"cannot reserve native configuration temporary directory");
    const auto data=temporary/"config";
    try {
        std::ofstream output(data,std::ios::binary);require(bool(output),"cannot create native configuration temporary file");
        output.write(reinterpret_cast<const char*>(bytes.data()),std::streamsize(bytes.size()));
        output.flush();require(bool(output),"cannot write native configuration temporary file");
        output.close();require(bool(output),"cannot close native configuration temporary file");
#ifdef _WIN32
        if(!MoveFileExW(data.c_str(),path_.c_str(),MOVEFILE_REPLACE_EXISTING|MOVEFILE_WRITE_THROUGH))
            throw std::runtime_error("cannot replace native configuration file (Win32 error "+std::to_string(GetLastError())+")");
#else
        fs::rename(data,path_);
#endif
        fs::remove(temporary);++commits_;
    } catch(...) {
        std::error_code ignored;fs::remove(data,ignored);fs::remove(temporary,ignored);throw;
    }
}
}

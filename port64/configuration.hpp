#pragma once
#include "menu_state.hpp"
#include <array>
#include <cstdint>
#include <filesystem>
#include <vector>

namespace th04::portable::configuration {
using Bytes=std::vector<std::uint8_t>;
using Options=std::array<std::uint8_t,6>;
enum class IO {open,seek,read,write,close};
struct Operation {IO kind;unsigned a=0,b=0;Bytes data;};
struct Result {Options options{};Bytes file;std::vector<Operation> operations;};
// OP's load corrects unsigned resident fields; rank/Turbo are copied raw.
Result load(const Bytes& file);
Result save(const Bytes& file,const Options& options,bool exiting);
std::uint8_t checksum(const Options& options);
Options encode(const menu::Options& options);
menu::Options decode(const Options& options);

// Independent host MIKO.CFG. Segment/debug bytes are opaque metadata here;
// they never become host pointers. Saves publish at writer close atomically.
class HostStore {
public:
    explicit HostStore(std::filesystem::path directory);
    menu::Options options() const {return options_;}
    const Bytes& bytes() const {return bytes_;}
    const std::filesystem::path& path() const {return path_;}
    bool repaired() const {return repaired_;}
    bool setup_required() const {return setup_required_;}
    unsigned commits() const {return commits_;}
    void save(const menu::Options& options,bool exiting);
    // Finishes the in-memory OP setup. Publication remains at an actual
    // game/demo entry or OP exit; closing an unfinished setup retains rankFF.
    void complete_setup(std::uint8_t bgm,std::uint8_t se);
private:
    void commit(const Bytes& bytes);
    std::filesystem::path path_;
    Bytes bytes_;
    menu::Options options_{};
    bool repaired_=false;
    bool setup_required_=false;
    unsigned commits_=0;
};
}

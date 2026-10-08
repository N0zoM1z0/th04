#pragma once
#include "score_file.hpp"
#include <filesystem>

namespace th04::portable::score_file {
// Separate from the read-only HDI. Replays ordered I/O, committing a complete
// pending file only when the original writer closes. Failed writes propagate.
class HostStore {
public:
    explicit HostStore(std::filesystem::path directory);
    File& file() { return file_; }
    const std::filesystem::path& path() const { return path_; }
    unsigned commits() const { return commits_; }
    void apply(const Operation&);
    static std::filesystem::path default_directory();
private:
    void commit();
    std::filesystem::path path_;
    Bytes pending_;
    File file_;
    std::size_t position_=0;
    bool opened_=false,dirty_=false;
    OpenMode mode_=OpenMode::read;
    unsigned commits_=0;
};
} // namespace th04::portable::score_file

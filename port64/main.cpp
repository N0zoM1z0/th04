// Native 64-bit TH04 resource bring-up. No DOS executable or game assets are
// embedded: the caller supplies their own original HDI or loose PAR archive.
#include <algorithm>
#include <array>
#include <cstdint>
#include <fstream>
#include <filesystem>
#include <iomanip>
#include <iostream>
#include <iterator>
#include <stdexcept>
#include <string>
#include <vector>

#include "view.hpp"

static void require(bool ok, const char* reason) {
    if (!ok) throw std::runtime_error(reason);
}

static uint16_t le16(const Bytes& b, size_t p) {
    require(p <= b.size() && b.size() - p >= 2, "short LE16 field");
    return uint16_t(b[p] | (uint16_t(b[p + 1]) << 8));
}

static uint32_t le32(const Bytes& b, size_t p) {
    return uint32_t(le16(b, p)) | (uint32_t(le16(b, p + 2)) << 16);
}

static void put16(Bytes& b, size_t p, uint16_t v) {
    b[p] = uint8_t(v); b[p + 1] = uint8_t(v >> 8);
}

static void put32(Bytes& b, size_t p, uint32_t v) {
    put16(b, p, uint16_t(v)); put16(b, p + 2, uint16_t(v >> 16));
}

static Bytes read_file(const std::string& name) {
    std::ifstream in(name, std::ios::binary);
    require(bool(in), "cannot open input file");
    Bytes b((std::istreambuf_iterator<char>(in)), std::istreambuf_iterator<char>());
    require(!b.empty(), "empty input file");
    return b;
}

static void write_file(const std::string& name, const Bytes& b) {
    std::ofstream out(name, std::ios::binary);
    require(bool(out), "cannot open output file");
    out.write(reinterpret_cast<const char*>(b.data()), std::streamsize(b.size()));
    require(bool(out), "cannot write output file");
}

class Fat12 {
public:
    explicit Fat12(const Bytes& image) : b(image) {
        constexpr size_t p = 38912;
        require(b.size() >= p + 512, "short PC-98 HDI");
        sector = le16(b, p + 11);
        cluster_sectors = b[p + 13];
        const auto reserved = le16(b, p + 14);
        const auto fats = b[p + 16];
        const auto entries = le16(b, p + 17);
        const auto sectors = le16(b, p + 19);
        const auto fat_sectors = le16(b, p + 22);
        require(sector == 1024 && cluster_sectors == 8 && reserved == 1 &&
                fats == 2 && entries == 1536 && sectors == 20706 &&
                fat_sectors == 4, "unexpected TH04 FAT12 geometry");
        require(p + size_t(sectors) * sector <= b.size(), "FAT12 volume truncated");
        fat_start = p + size_t(reserved) * sector;
        const size_t fat_bytes = size_t(fat_sectors) * sector;
        require(std::equal(b.begin() + fat_start, b.begin() + fat_start + fat_bytes,
                           b.begin() + fat_start + fat_bytes), "FAT mirrors disagree");
        root = fat_start + size_t(fats) * fat_bytes;
        const size_t root_sectors = (size_t(entries) * 32 + sector - 1) / sector;
        data = root + root_sectors * sector;
        max_cluster = 1 + (sectors - reserved - fats * fat_sectors - root_sectors) / cluster_sectors;
    }

    Bytes op_archive() const {
        return game_file(std::string("\x8c\xb6\x91\x7a\x8b\xbd" "EDDAT", 11));
    }

    Bytes main_archive() const {
        return game_file(std::string("\x93\x8c\x95\xfb\x8c\xb6\x91\x7a\x8b\xbd ", 11));
    }

    Bytes game_file(const std::string& name) const {
        const size_t dir = find({root}, "GENSO      ");
        const auto dirs = chain(le16(b, dir + 26));
        std::vector<size_t> offsets;
        for (auto c : dirs) offsets.push_back(cluster_offset(c));
        // CP932 short name of the original OP/ending resource archive.
        const size_t file = find(offsets, name);
        return file_bytes(le16(b, file + 26), le32(b, file + 28));
    }

private:
    const Bytes& b;
    size_t sector{}, cluster_sectors{}, fat_start{}, root{}, data{}, max_cluster{};

    uint16_t next(uint16_t cluster) const {
        require(cluster >= 2 && cluster <= max_cluster, "FAT cluster out of range");
        uint16_t word = le16(b, fat_start + cluster + cluster / 2);
        return cluster & 1 ? (word >> 4) & 0xfff : word & 0xfff;
    }

    std::vector<uint16_t> chain(uint16_t first) const {
        std::vector<uint16_t> result;
        std::vector<bool> seen(max_cluster + 1);
        for (uint16_t c = first; c < 0xff8; c = next(c)) {
            require(c >= 2 && c <= max_cluster && !seen[c], "invalid FAT chain");
            seen[c] = true;
            result.push_back(c);
        }
        require(!result.empty(), "empty FAT chain");
        return result;
    }

    size_t cluster_offset(uint16_t c) const {
        require(c >= 2 && c <= max_cluster, "cluster out of range");
        const size_t at = data + (size_t(c) - 2) * sector * cluster_sectors;
        require(at <= b.size() && b.size() - at >= sector * cluster_sectors,
                "cluster outside image");
        return at;
    }

    size_t find(const std::vector<size_t>& dirs, const std::string& name) const {
        require(name.size() == 11, "FAT name must be 11 bytes");
        for (size_t start : dirs) {
            const size_t end = start + (start == root ? 1536 * 32 : sector * cluster_sectors);
            require(end <= b.size(), "directory outside image");
            for (size_t at = start; at < end; at += 32) {
                if (b[at] == 0) break;
                if (b[at] != 0xe5 && b[at + 11] != 0x0f &&
                    std::equal(name.begin(), name.end(), b.begin() + at,
                               [](char a, uint8_t c) { return uint8_t(a) == c; })) return at;
            }
        }
        throw std::runtime_error("GENSO or OP archive missing from HDI");
    }

    Bytes file_bytes(uint16_t first, size_t size) const {
        const auto clusters = chain(first);
        const size_t cluster_bytes = sector * cluster_sectors;
        require(size <= clusters.size() * cluster_bytes, "file exceeds FAT chain");
        Bytes out;
        out.reserve(size);
        for (uint16_t c : clusters) {
            const auto at = cluster_offset(c);
            const auto n = std::min(size - out.size(), cluster_bytes);
            out.insert(out.end(), b.begin() + at, b.begin() + at + n);
            if (out.size() == size) break;
        }
        return out;
    }
};

static Bytes archive_member(const Bytes& b, const std::string& wanted,
                            std::map<std::string,Bytes>* sound_members=nullptr) {
    require(b.size() >= 16, "short PAR archive");
    const auto count = le16(b, 4);
    const auto table_size = le16(b, 0);
    require(count > 0 && table_size == (count + 1) * 32 &&
            16 + size_t(table_size) <= b.size() && le16(b, 6) <= 255,
            "invalid PAR directory");
    Bytes directory(b.begin() + 16, b.begin() + 16 + table_size);
    uint8_t key = uint8_t(le16(b, 6));
    for (auto& v : directory) {
        v ^= key;
        key = uint8_t(key - v);
    }
    require(std::all_of(directory.end() - 32, directory.end(),
                        [](uint8_t v) { return v == 0; }), "PAR terminal record changed");
    for (size_t i = 0; i < count; ++i) {
        const size_t at = i * 32;
        const auto first = directory.begin() + at + 3;
        const auto last = std::find(first, first + 13, 0);
        const std::string name(first, last);
        const auto extension=name.size()>=4 ? name.substr(name.size()-4) : std::string{};
        if (name != wanted && !(sound_members && (extension==".M26" || extension==".M86" || extension==".EFC" || extension==".EFS"))) continue;
        const auto type = le16(directory, at);
        const auto aux = directory[at + 2];
        const size_t packed_size = le16(directory, at + 16);
        const size_t logical_size = le16(directory, at + 18);
        const size_t offset = le32(directory, at + 20);
        require(offset >= 16 + size_t(table_size) && offset <= b.size() &&
                packed_size <= b.size() - offset, "PAR member outside archive");
        Bytes out;
        int previous = -1;
        for (size_t p = offset; p < offset + packed_size; ++p) {
            uint8_t value = b[p] ^ aux;
            out.push_back(value);
            if (type == 0x9595 && value == previous) {
                require(++p < offset + packed_size, "PAR repeat count missing");
                const uint8_t repeats = b[p] ^ aux;
                out.insert(out.end(), repeats, value);
            }
            previous = value;
            require(out.size() <= logical_size + 1, "PAR expansion exceeds length");
        }
        require(type == 0xf388 || type == 0x9595, "unknown PAR compression");
        require(out.size() == logical_size || out.size() == logical_size + 1,
                "PAR expanded size disagrees with directory");
        out.resize(logical_size);
        if(sound_members) {
            const auto previous=sound_members->find(name);
            if(previous!=sound_members->end())require(previous->second==out,"conflicting sound resource across archives");
            else sound_members->emplace(name,std::move(out));
            continue;
        }
        return out;
    }
    if(sound_members)return {};
    throw std::runtime_error("PAR member missing: " + wanted);
}

static uint32_t fnv32(const Bytes& b) {
    uint32_t hash = 2166136261u;
    for (auto v : b) hash = (hash ^ v) * 16777619u;
    return hash;
}

static Bytes bmp24(const PiImage& img) {
    const size_t stride = (size_t(img.width) * 3 + 3) & ~size_t(3);
    require(stride * img.height <= UINT32_MAX - 54, "BMP size overflow");
    Bytes bmp(54 + stride * img.height);
    bmp[0] = 'B'; bmp[1] = 'M';
    put32(bmp, 2, uint32_t(bmp.size()));
    put32(bmp, 10, 54); put32(bmp, 14, 40);
    put32(bmp, 18, img.width); put32(bmp, 22, img.height);
    put16(bmp, 26, 1); put16(bmp, 28, 24);
    put32(bmp, 34, uint32_t(stride * img.height));
    for (size_t y = 0; y < img.height; ++y) {
        const size_t row = 54 + (img.height - y - 1) * stride;
        for (size_t x = 0; x < img.width; ++x) {
            const uint8_t packed = img.pixels[y * img.width / 2 + x / 2];
            const unsigned color = x & 1 ? packed & 15 : packed >> 4;
            for (unsigned c = 0; c < 3; ++c)
                bmp[row + x * 3 + c] = uint8_t((img.palette[color * 3 + (2 - c)] >> 4) * 17);
        }
    }
    return bmp;
}

int main(int argc, char** argv) {
    try {
        std::string hdi, archive, member, output, title_screenshot;
        std::string options_screenshot, character_screenshot, shot_screenshot;
        std::string handoff_screenshot, main_screenshot, shooting_screenshots, combat_screenshots, midboss_screenshots,orange_screenshots,dialog_screenshots,stage2_screenshots,kurumi_screenshots,stage3_screenshots,elly_screenshots,stage4_screenshots,reimu_screenshots,marisa_screenshots,stage5_screenshots,yuuka5_screenshots,stage6_screenshots,ending_screenshots,font_bitmap;
        bool window_route_advice=false;
        bool title_window = false,muted=true,audio_requested=false,mute_requested=false,offline_requested=false;
        std::string pmd_driver="pmd",opna_rom,resident_sound_checks,window_trace;
        std::string configuration_checks,setup_checks,sound_checks,sound_scene_checks,startup_checks,natural_route_checks;
        std::string save_directory,registration_checks,gameover_checks,score_route_checks,bomb_checks,extra_checks,mugetsu_checks,gengetsu_checks,extra_clear_checks,extra_maine_checks,op_score_checks,op_ranking_checks,op_music_checks,demo_checks;
        for (int i = 1; i < argc; ++i) {
            const std::string arg = argv[i];
            if (arg == "--window-route-advice") {window_route_advice=true;continue;}
            if (arg == "--title") { title_window = true; continue; }
            if (arg == "--mute") { mute_requested=true;continue; }
            if (arg == "--audio") { audio_requested=true;continue; }
            require(i + 1 < argc, "each option needs a value");
            const std::string value = argv[++i];
            if(arg.find("-checks")!=std::string::npos || arg.find("-screenshot")!=std::string::npos ||
               arg=="--member" || arg=="--output")offline_requested=true;
            if (arg == "--hdi") hdi = value;
            else if(arg=="--pmd-driver")pmd_driver=value;
            else if(arg=="--window-trace")window_trace=value;
            else if(arg=="--opna-rom")opna_rom=value;
            else if(arg=="--resident-sound-checks")resident_sound_checks=value;
            else if(arg=="--startup-checks")startup_checks=value;
            else if(arg=="--natural-route-checks")natural_route_checks=value;
            else if(arg=="--save-dir")save_directory=value;
            else if(arg=="--configuration-checks")configuration_checks=value;
            else if(arg=="--setup-checks")setup_checks=value;
            else if(arg=="--sound-checks")sound_checks=value;
            else if(arg=="--sound-scene-checks")sound_scene_checks=value;
            else if(arg=="--registration-checks")registration_checks=value;
            else if(arg=="--gameover-checks")gameover_checks=value;
            else if(arg=="--extra-checks")extra_checks=value;
            else if(arg=="--mugetsu-checks")mugetsu_checks=value;
            else if(arg=="--gengetsu-checks")gengetsu_checks=value;
            else if(arg=="--extra-clear-checks")extra_clear_checks=value;
            else if(arg=="--extra-maine-checks")extra_maine_checks=value;
            else if(arg=="--op-score-checks")op_score_checks=value;
            else if(arg=="--op-ranking-checks")op_ranking_checks=value;
            else if(arg=="--op-music-checks")op_music_checks=value;
            else if(arg=="--demo-checks")demo_checks=value;
            else if(arg=="--bomb-checks")bomb_checks=value;
            else if(arg=="--score-route-checks")score_route_checks=value;
            else if (arg == "--archive") archive = value;
            else if (arg == "--member") member = value;
            else if (arg == "--output") output = value;
            else if (arg == "--title-screenshot") title_screenshot = value;
            else if (arg == "--options-screenshot") options_screenshot = value;
            else if (arg == "--character-screenshot") character_screenshot = value;
            else if (arg == "--shot-screenshot") shot_screenshot = value;
            else if (arg == "--handoff-screenshot") handoff_screenshot = value;
            else if (arg == "--main-screenshot") main_screenshot = value;
            else if (arg == "--shooting-screenshots") shooting_screenshots = value;
            else if (arg == "--combat-screenshots") combat_screenshots = value;
            else if (arg == "--midboss-screenshots") midboss_screenshots = value;
            else if (arg == "--orange-screenshots") orange_screenshots = value;
            else if (arg == "--dialog-screenshots") dialog_screenshots = value;
            else if (arg == "--stage2-screenshots") stage2_screenshots = value;
            else if (arg == "--marisa-screenshots") marisa_screenshots = value;
            else if (arg == "--reimu-screenshots") reimu_screenshots = value;
            else if (arg == "--stage5-screenshots") stage5_screenshots = value;
            else if (arg == "--ending-screenshots") ending_screenshots = value;
            else if (arg == "--stage6-screenshots") stage6_screenshots = value;
            else if (arg == "--yuuka5-screenshots") yuuka5_screenshots = value;
            else if (arg == "--stage4-screenshots") stage4_screenshots = value;
            else if (arg == "--elly-screenshots") elly_screenshots = value;
            else if (arg == "--stage3-screenshots") stage3_screenshots = value;
            else if (arg == "--kurumi-screenshots") kurumi_screenshots = value;
            else if (arg == "--font-bmp") font_bitmap = value;
            else throw std::runtime_error("unknown option: " + arg);
        }
        const bool title = title_window || !natural_route_checks.empty() || !startup_checks.empty() || !resident_sound_checks.empty() || !sound_checks.empty() || !sound_scene_checks.empty() || !setup_checks.empty() || !configuration_checks.empty() || ((!demo_checks.empty() || !op_music_checks.empty()) || !op_ranking_checks.empty()) || !op_score_checks.empty() || !extra_maine_checks.empty() || !extra_clear_checks.empty() || !gengetsu_checks.empty() || !mugetsu_checks.empty() || !extra_checks.empty() || !bomb_checks.empty() || !score_route_checks.empty() || !gameover_checks.empty() || !registration_checks.empty() || !title_screenshot.empty() ||
            !options_screenshot.empty() || !character_screenshot.empty() ||
            !shot_screenshot.empty() || !handoff_screenshot.empty() || !main_screenshot.empty() ||
            !shooting_screenshots.empty() || !combat_screenshots.empty() || !midboss_screenshots.empty() || !orange_screenshots.empty() || !dialog_screenshots.empty() || !stage2_screenshots.empty() || !kurumi_screenshots.empty() || !stage3_screenshots.empty() || !elly_screenshots.empty() || !stage4_screenshots.empty() || !reimu_screenshots.empty() || !marisa_screenshots.empty() || !stage5_screenshots.empty() || !yuuka5_screenshots.empty() || !stage6_screenshots.empty() || !ending_screenshots.empty();
        require((!hdi.empty()) != (!archive.empty()) && (title || !member.empty()) &&
                !(title && (!member.empty() || !output.empty())),
                "usage: th04-port64 (--hdi FILE | --archive FILE) "
                "[--member NAME --output BMP | --title "
                "[--title-screenshot BMP] [--options-screenshot BMP] "
                "[--character-screenshot BMP] [--shot-screenshot BMP] "
                "[--handoff-screenshot BMP] [--main-screenshot BMP] [--shooting-screenshots DIR] [--combat-screenshots DIR] [--midboss-screenshots DIR] [--orange-screenshots DIR] [--dialog-screenshots DIR] [--stage2-screenshots DIR] [--kurumi-screenshots DIR] [--stage3-screenshots DIR] [--elly-screenshots DIR] [--stage4-screenshots DIR] [--reimu-screenshots DIR] [--marisa-screenshots DIR] [--stage5-screenshots DIR] [--yuuka5-screenshots DIR] [--stage6-screenshots DIR] [--ending-screenshots DIR] [--font-bmp FILE] [--save-dir DIR] [--registration-checks DIR] [--gameover-checks DIR] [--sound-checks DIR] [--score-route-checks DIR] [--resident-sound-checks DIR] [--startup-checks DIR] [--natural-route-checks DIR] [--pmd-driver pmd|pmd86|pmdb2|none] [--opna-rom FILE] [--window-trace DIR] [--window-route-advice] [--audio] [--mute]]");
        require(natural_route_checks.empty() || (!title_window && startup_checks.empty() && !hdi.empty() && !save_directory.empty()),
                "natural routes require headless --hdi and --save-dir without --startup-checks");
        muted=!audio_requested || mute_requested;
        require(muted || (title_window && !offline_requested),"--audio requires an interactive --title; diagnostics must remain --mute");
        require(window_trace.empty() || (title_window && muted && !offline_requested && !std::filesystem::exists(window_trace)),"--window-trace requires an interactive muted window and fresh output");
        require(!window_route_advice || !window_trace.empty(),"--window-route-advice requires a muted window trace");
        const auto par = hdi.empty() ? read_file(archive) : Fat12(read_file(hdi)).op_archive();
        require(pmd_driver=="none" || pmd_driver=="pmd" || pmd_driver=="pmd86" || pmd_driver=="pmdb2","PMD driver must be none, pmd, pmd86 or pmdb2");
        require(opna_rom.empty() || pmd_driver=="pmd86" || pmd_driver=="pmdb2","rhythm ROM belongs to an OPNA profile");
        if (title) {
            MainAssets main_assets;
            main_assets.save_directory=save_directory;main_assets.muted=muted;main_assets.window_trace=window_trace;main_assets.window_route_advice=window_route_advice;
            main_assets.configuration_checks=configuration_checks;
            main_assets.setup_checks=setup_checks;
            main_assets.sound_checks=sound_checks;main_assets.sound_scene_checks=sound_scene_checks;
            main_assets.resident_sound_checks=resident_sound_checks;
            main_assets.full_startup=title_window || !startup_checks.empty() || !natural_route_checks.empty();main_assets.startup_checks=startup_checks;
            main_assets.natural_route_checks=natural_route_checks;
            if(main_assets.full_startup) {
                auto& startup=main_assets.startup;startup.logo=decode_pi(archive_member(par,"ZUN00.PI"));startup.menu=decode_pi(archive_member(par,"OP1.PI"));
                for(unsigned i=0;i<6;++i)startup.slides[i]=decode_pi(archive_member(par,"OP"+std::to_string(5-i)+"B.PI"));
                constexpr unsigned order[]={2,4,1,3};for(unsigned i=0;i<4;++i)startup.fireworks[i]=archive_member(par,"ZUN0"+std::to_string(order[i])+".BFT");
            }
            if (!hdi.empty()) {
                const auto image = read_file(hdi);
                const auto game = Fat12(image).main_archive();
                main_assets.main_effects=archive_member(game,"MIKO.EFS");
                archive_member(game,"",&main_assets.sound_resources);
                archive_member(par,"",&main_assets.sound_resources);
                if(pmd_driver!="none") {
                    require(pmd_driver=="pmd" || !opna_rom.empty(),"OPNA profile requires --opna-rom FILE");
                    const auto board=pmd_driver=="pmd" ? th04::portable::pmd::Board::fm26 :
                        pmd_driver=="pmd86" ? th04::portable::pmd::Board::speakboard : th04::portable::pmd::Board::fm86;
                    main_assets.pmd_profile=th04::portable::sound::PmdProfile{board,pmd_driver=="pmd" ? 4000000u : 8000000u,
                        pmd_driver=="pmd" ? Bytes{} : read_file(opna_rom)};
                }
                for(unsigned i=0;i<4;++i)
                    main_assets.replays[i]=archive_member(game,"DEMO"+std::to_string(i+1)+".REC");
                main_assets.reimu = archive_member(game, "MIKO.BFT");
                main_assets.marisa = archive_member(game, "MARI.BFT");
                main_assets.items = archive_member(game, "MIKO16.BFT");
                for(unsigned c=0;c<2;++c) {
                    main_assets.bomb_tiles[c]=archive_member(game,"BB"+std::to_string(c)+".BB");
                    main_assets.bomb_pictures[c]=archive_member(game,"BB"+std::to_string(c)+".CDG");
                }
                main_assets.enemies = archive_member(game, "MIKO32.BFT");
                main_assets.stage_tiles = archive_member(game, "ST00.BFT");
                main_assets.boss_tiles = archive_member(game, "ST00.BMT");
                main_assets.explosion_sprite=archive_member(game,"MIKOD.BFT");
                main_assets.orange_background=archive_member(game,"ST00BK.CDG");
                main_assets.orange_transition=archive_member(game,"ST00.BB");
                main_assets.dialog_scripts={archive_member(game,"_DM00.TXT"),archive_member(game,"_DM10.TXT")};
                main_assets.player_faces={archive_member(game,"KAO0.CD2"),archive_member(game,"KAO1.CD2")};
                main_assets.boss_faces=archive_member(game,"BSS0.CD2");main_assets.gaiji=archive_member(game,"GAMEFT.BFT");
                for(const std::string name:{"ST00.BB1","ST00.BB2","ST02.BB1","ST02.BB2","ST03.BBT","ST03B.BBT","ST03B21.BBT","ST03B22.BBT","ST04.BB1","ST04.BB2","ST05.BB1","ST05.BB2","ST05.BB3","ST05.BB4","ST05.BB5","ST05.BB6","ST05.BB7","ST05.BB9","ST06.BB1","ST06.BB2","ST06.BB3"}) main_assets.dialog_sprites.emplace(name,archive_member(game,name));
                if(!font_bitmap.empty()) main_assets.font_bitmap=read_file(font_bitmap);
                else { std::ifstream font("FREECG98.bmp",std::ios::binary);if(font) main_assets.font_bitmap={std::istreambuf_iterator<char>(font),{}}; }
                if(title_window || !natural_route_checks.empty() || !startup_checks.empty() || !resident_sound_checks.empty() || !sound_checks.empty() || !sound_scene_checks.empty() || !setup_checks.empty() || !configuration_checks.empty() || ((!demo_checks.empty() || !op_music_checks.empty()) || !op_ranking_checks.empty()) || !op_score_checks.empty() || !extra_maine_checks.empty() || !ending_screenshots.empty() || !registration_checks.empty() || !gameover_checks.empty() || !score_route_checks.empty()) {
                    auto& ending=main_assets.ending;
                    ending.font_bitmap=main_assets.font_bitmap;
                    ending.gaiji=archive_member(par,"GAMEFT.BFT");
                    auto& registration=main_assets.registration;
                    registration.graphics.font_bitmap=main_assets.font_bitmap;
                    registration.graphics.gaiji=ending.gaiji;
                    registration.graphics.pictures.emplace("HI01.PI",decode_pi(archive_member(par,"HI01.PI")));
                    registration.numerals=archive_member(par,"SCNUM2.BFT");
                    auto& ranking=main_assets.ranking;
                    ranking.graphics=registration.graphics;
                    ranking.graphics.pictures.emplace("OP1.PI",decode_pi(archive_member(par,"OP1.PI")));
                    ranking.numerals=archive_member(par,"SCNUM.BFT");
                    ranking.rank_labels=archive_member(par,"HI_M.BFT");
                    main_assets.music.graphics=registration.graphics;
                    main_assets.music.graphics.pictures.emplace("MUSIC.PI",decode_pi(archive_member(par,"MUSIC.PI")));
                    main_assets.music.comments=archive_member(par,"_MUSIC.TXT");
                    main_assets.setup.graphics=registration.graphics;
                    main_assets.setup.graphics.pictures.emplace("MS.PI",decode_pi(archive_member(par,"MS.PI")));
                    main_assets.setup.windows=archive_member(par,"MSWIN.BFT");
                    // Attested MAINE registration notice; preserve Shift-JIS
                    // bytes instead of translating the original graphics.
                    registration.non_turbo_message=
                        "\x83\x58\x83\x8D\x81\x5B\x83\x82\x81\x5B\x83\x68\x82\xC5\x82\xCC"
                        "\x83\x76\x83\x8C\x83\x43\x82\xC5\x82\xCD\x81\x41\x83\x58\x83\x52"
                        "\x83\x41\x82\xCD\x8B\x4C\x98\x5E\x82\xB3\x82\xEA\x82\xDC\x82\xB9\x82\xF1";
                    for(unsigned character=0;character<2;++character) for(unsigned shot=0;shot<2;++shot)
                        for(bool bad:{false,true}) {
                            const auto name=th04::portable::cutscene::script_name(character,shot,bad);
                            ending.scripts.emplace(name,archive_member(par,name));
                        }
                    for(unsigned i=0;i<17;++i) {
                        std::ostringstream name;name<<"ED"<<std::setw(2)<<std::setfill('0')<<i<<".PI";
                        ending.pictures.emplace(name.str(),decode_pi(archive_member(par,name.str())));
                    }
                    ending.pictures.emplace("UDE.PI",decode_pi(archive_member(par,"UDE.PI")));
                    ending.scripts.emplace("_UDE.TXT",archive_member(par,"_UDE.TXT"));
                    for(unsigned character=0;character<2;++character)for(unsigned rank=0;rank<5;++rank) {
                        const auto name="CONG"+std::to_string(character)+std::to_string(rank)+".PI";
                        ending.pictures.emplace(name,decode_pi(archive_member(par,name)));
                    }
                    for(unsigned i=1;i<=2;++i) {
                        const auto name="SFF"+std::to_string(i)+".PI";
                        main_assets.staff_roll.pictures.emplace(name,decode_pi(archive_member(par,name)));
                    }
                    for(unsigned i=1;i<=9;++i)for(const auto suffix:{".CDG","B.CDG"}) {
                        const auto name="SFF"+std::to_string(i)+suffix;
                        main_assets.staff_roll.sprites.emplace(name,archive_member(par,name));
                    }
                }
                main_assets.reimu_map_tiles = archive_member(game, "ST00.MPN");
                main_assets.marisa_map_tiles = archive_member(game, "ST10.MPN");
                main_assets.map = archive_member(game, "ST00.MAP");
                main_assets.standard = archive_member(game, "ST00.STD");
                auto& second=main_assets.stage2;
                second.stage_tiles=archive_member(game,"ST01.BFT");second.boss_tiles=archive_member(game,"ST01.BMT");
                second.backdrop=archive_member(game,"ST01BK.CDG");second.transition=archive_member(game,"ST01.BB");
                second.boss_faces=archive_member(game,"BSS1.CD2");second.map_tiles=archive_member(game,"ST01.MPN");
                second.map=archive_member(game,"ST01.MAP");second.standard=archive_member(game,"ST01.STD");
                second.dialog_scripts={archive_member(game,"_DM01.TXT"),archive_member(game,"_DM11.TXT")};
                auto& third=main_assets.stage3;
                third.stage_tiles=archive_member(game,"ST02.BFT");third.boss_tiles=archive_member(game,"ST02.BMT");
                third.backdrop=archive_member(game,"ST02BK.CDG");third.transition=archive_member(game,"ST02.BB");
                third.boss_faces=archive_member(game,"BSS2.CD2");third.map_tiles=archive_member(game,"ST02.MPN");
                third.map=archive_member(game,"ST02.MAP");third.standard=archive_member(game,"ST02.STD");
                third.dialog_scripts={archive_member(game,"_DM02.TXT"),archive_member(game,"_DM12.TXT")};
                for(unsigned character=0;character<2;++character) {
                    auto& fourth=main_assets.stage4[character];
                    fourth.stage_tiles=archive_member(game,"ST03.BFT");fourth.boss_tiles=archive_member(game,"ST03.BMT");
                    fourth.backdrop=archive_member(game,character==0 ? "ST03BK2.CDG" : "ST03BK.CDG");
                    fourth.boss_faces=archive_member(game,character==0 ? "KAO3.CD2" : "KAO2.CD2");
                    fourth.transition=archive_member(game,"ST03.BB");fourth.map_tiles=archive_member(game,"ST03.MPN");
                    fourth.map=archive_member(game,"ST03.MAP");fourth.standard=archive_member(game,"ST03.STD");
                    fourth.dialog_scripts={archive_member(game,"_DM03.TXT"),archive_member(game,"_DM13.TXT")};
                }
                auto& fifth=main_assets.stage5;
                fifth.stage_tiles=archive_member(game,"ST04.BFT");
                fifth.backdrop=archive_member(game,"ST04BK.CDG");fifth.stars=archive_member(game,"ST04.CDG");
                fifth.boss_faces=archive_member(game,"BSS4.CD2");fifth.transition=archive_member(game,"ST04.BB");
                fifth.map_tiles=archive_member(game,"ST04.MPN");fifth.map=archive_member(game,"ST04.MAP");fifth.standard=archive_member(game,"ST04.STD");
                fifth.dialog_scripts={archive_member(game,"_DM04.TXT"),archive_member(game,"_DM14.TXT")};
                fifth.bad_dialog_scripts={archive_member(game,"_DM04B.TXT"),archive_member(game,"_DM14B.TXT")};
                auto& sixth=main_assets.stage6;
                sixth.stage_tiles=archive_member(game,"ST05.BFT");sixth.transition=archive_member(game,"ST05.BB");
                sixth.boss_faces=archive_member(game,"BSS5.CD2");sixth.map_tiles=archive_member(game,"ST05.MPN");
                sixth.map=archive_member(game,"ST05.MAP");sixth.standard=archive_member(game,"ST05.STD");
                auto& extra=main_assets.extra;
                extra.stage_tiles=archive_member(game,"ST06.BFT");extra.transition=archive_member(game,"ST06.BB");
                extra.backdrop=archive_member(game,"ST06BK.CDG");extra.boss_faces=archive_member(game,"BSS6.CD2");
                extra.map_tiles=archive_member(game,"ST06.MPN");extra.map=archive_member(game,"ST06.MAP");extra.standard=archive_member(game,"ST06.STD");
                extra.dialog_scripts[0]=extra.dialog_scripts[1]=archive_member(game,"_DM06.TXT");
                main_assets.gengetsu_backdrop=archive_member(game,"ST06BK2.CDG");
                main_assets.gengetsu_transition=archive_member(game,"ST06B.BB");
                main_assets.extra_defeat_faces={archive_member(game,"BSS7.CD2"),archive_member(game,"BSS8.CD2")};
                sixth.dialog_scripts={archive_member(game,"_DM05.TXT"),archive_member(game,"_DM15.TXT")};
            }
            require((setup_checks.empty() && configuration_checks.empty() && demo_checks.empty() && op_music_checks.empty() && op_ranking_checks.empty() && op_score_checks.empty() && extra_maine_checks.empty() && extra_clear_checks.empty() && gengetsu_checks.empty() && mugetsu_checks.empty() && extra_checks.empty() && main_screenshot.empty() && shooting_screenshots.empty() && combat_screenshots.empty() && midboss_screenshots.empty() && orange_screenshots.empty() && dialog_screenshots.empty() && stage2_screenshots.empty() && kurumi_screenshots.empty() && stage3_screenshots.empty() && elly_screenshots.empty() && stage4_screenshots.empty() && reimu_screenshots.empty() && marisa_screenshots.empty() && stage5_screenshots.empty() && yuuka5_screenshots.empty() && stage6_screenshots.empty() && ending_screenshots.empty()) || !main_assets.reimu.empty(),
                    "MAIN screenshots require a complete TH04 HDI");
            const auto bg = decode_pi(archive_member(par, "OP1.PI"));
            run_title(
                bg, archive_member(par, "SFT1.CD2"),
                archive_member(par, "SFT2.CD2"),
                archive_member(par, "CAR.CD2"),
                decode_pi(archive_member(par, "SLB1.PI")),
                archive_member(par, "SL.CD2"), main_assets, title_screenshot,
                options_screenshot, character_screenshot, shot_screenshot,
                handoff_screenshot, main_screenshot, shooting_screenshots, combat_screenshots, midboss_screenshots,orange_screenshots,dialog_screenshots,stage2_screenshots,kurumi_screenshots,stage3_screenshots,elly_screenshots,stage4_screenshots,reimu_screenshots,marisa_screenshots,stage5_screenshots,yuuka5_screenshots,stage6_screenshots,ending_screenshots,registration_checks,gameover_checks,score_route_checks,bomb_checks,extra_checks,mugetsu_checks,gengetsu_checks,extra_clear_checks,extra_maine_checks,op_score_checks,op_ranking_checks,op_music_checks,demo_checks,title_window
            );
            return 0;
        }
        const auto pi = decode_pi(archive_member(par, member));
        if (!output.empty()) write_file(output, bmp24(pi));
        std::cout << member << " " << pi.width << "x" << pi.height << " FNV32="
                  << std::uppercase << std::hex << std::setw(8) << std::setfill('0')
                  << fnv32(pi.pixels) << std::endl;
        return 0;
    } catch (const std::exception& e) {
        std::cerr << "th04-port64: " << e.what() << std::endl;
        return 1;
    }
}

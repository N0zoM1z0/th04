#!/usr/bin/env bash
# Download and install the exact Ghidra/JDK pair used by TH04 analysis.
set -euo pipefail

repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
tools_root="$repo_root/.tools"
downloads="$tools_root/downloads"

ghidra_asset=ghidra_12.1.3_PUBLIC_20260817.zip
ghidra_url=https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_12.1.3_build/ghidra_12.1.3_PUBLIC_20260817.zip
ghidra_sha256=93a5d11a9ad510622acaaf908c556a7b9b764d338e78a7567f3689bf5081fd54
ghidra_size=569445154
ghidra_home="$tools_root/ghidra_12.1.3_PUBLIC"

jdk_asset=OpenJDK21U-jdk_x64_linux_hotspot_21.0.12.1_1.tar.gz
jdk_url=https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.12.1%2B1/OpenJDK21U-jdk_x64_linux_hotspot_21.0.12.1_1.tar.gz
jdk_sha256=ce79869e1307ed8ee1e2baa86a412b1eb5b75d10a01006d788a6f968bcfaee94
jdk_size=207473347
jdk_home="$tools_root/jdk-21.0.12.1+1"

for command_name in curl python3 sha256sum stat tar unzip; do
	command -v "$command_name" >/dev/null || {
		echo "missing prerequisite: $command_name" >&2
		exit 1
	}
done
if [[ "$(uname -m)" != x86_64 ]]; then
	echo "the pinned Temurin JDK asset supports Linux x86-64 only" >&2
	exit 1
fi

mkdir -p "$downloads"

download_checked() {
	local url=$1
	local destination=$2
	local expected_size=$3
	local expected_sha256=$4
	if [[ ! -f "$destination" ]]; then
		curl --fail --location --retry 3 --output "$destination" "$url"
	fi
	if [[ "$(stat -c '%s' "$destination")" != "$expected_size" ]]; then
		echo "download size mismatch: $destination" >&2
		exit 1
	fi
	echo "$expected_sha256  $destination" | sha256sum --check --status || {
		echo "download SHA-256 mismatch: $destination" >&2
		exit 1
	}
}

download_checked "$ghidra_url" "$downloads/$ghidra_asset" "$ghidra_size" "$ghidra_sha256"
download_checked "$jdk_url" "$downloads/$jdk_asset" "$jdk_size" "$jdk_sha256"

# Refuse archive traversal before invoking the platform extraction tools.
python3 - "$downloads/$ghidra_asset" "$downloads/$jdk_asset" <<'PY'
from pathlib import PurePosixPath
import posixpath
import sys
import tarfile
import zipfile


def safe(name: str) -> bool:
    path = PurePosixPath(name)
    return not path.is_absolute() and ".." not in path.parts


with zipfile.ZipFile(sys.argv[1]) as archive:
    bad = [item.filename for item in archive.infolist() if not safe(item.filename)]
    if bad:
        raise SystemExit(f"unsafe Ghidra archive path: {bad[0]}")
with tarfile.open(sys.argv[2], "r:gz") as archive:
    for item in archive.getmembers():
        if not safe(item.name):
            raise SystemExit(f"unsafe JDK archive path: {item.name}")
        if item.issym() or item.islnk():
            parent = PurePosixPath(item.name).parent
            link = PurePosixPath(item.linkname)
            target = PurePosixPath(posixpath.normpath(str(parent / link)))
            if link.is_absolute() or target.is_absolute() or target.parts[0] == "..":
                raise SystemExit(f"unsafe JDK archive link: {item.name} -> {item.linkname}")
PY

stage=""
cleanup() {
	if [[ -n "$stage" && -d "$stage" ]]; then
		rm -rf -- "$stage"
	fi
}
trap cleanup EXIT

if [[ ! -e "$ghidra_home" ]]; then
	stage=$(mktemp -d "$tools_root/.ghidra-stage.XXXXXX")
	unzip -q "$downloads/$ghidra_asset" -d "$stage"
	test -x "$stage/ghidra_12.1.3_PUBLIC/support/analyzeHeadless" || {
		echo "Ghidra archive did not produce the expected root" >&2
		exit 1
	}
	mv -- "$stage/ghidra_12.1.3_PUBLIC" "$ghidra_home"
	rmdir -- "$stage"
	stage=""
elif [[ ! -d "$ghidra_home" ]]; then
	echo "refusing non-directory Ghidra installation path: $ghidra_home" >&2
	exit 1
fi

if [[ ! -e "$jdk_home" ]]; then
	stage=$(mktemp -d "$tools_root/.jdk-stage.XXXXXX")
	tar -xzf "$downloads/$jdk_asset" -C "$stage"
	test -x "$stage/jdk-21.0.12.1+1/bin/java" || {
		echo "JDK archive did not produce the expected root" >&2
		exit 1
	}
	mv -- "$stage/jdk-21.0.12.1+1" "$jdk_home"
	rmdir -- "$stage"
	stage=""
elif [[ ! -d "$jdk_home" ]]; then
	echo "refusing non-directory JDK installation path: $jdk_home" >&2
	exit 1
fi

for stable_link in "$tools_root/ghidra" "$tools_root/jdk"; do
	if [[ -e "$stable_link" && ! -L "$stable_link" ]]; then
		echo "refusing to replace non-symlink stable tool path: $stable_link" >&2
		exit 1
	fi
done
ln -sfn -- "$(basename "$ghidra_home")" "$tools_root/ghidra"
ln -sfn -- "$(basename "$jdk_home")" "$tools_root/jdk"

python3 "$repo_root/scripts/attest_analysis_toolchain.py"
echo "TH04 analysis toolchain bootstrap complete"
echo "source scripts/tool-env.sh before unusual direct headless invocations"

#!/usr/bin/env bash
# Source this file before invoking the pinned TH04 headless analyzer by hand.

th04_repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
export GHIDRA_HOME="$th04_repo_root/.tools/ghidra"
export JAVA_HOME="$th04_repo_root/.tools/jdk"
export XDG_CONFIG_HOME="$th04_repo_root/.analysis/ghidra/config"
export XDG_CACHE_HOME="$th04_repo_root/.analysis/ghidra/cache"
export XDG_DATA_HOME="$th04_repo_root/.analysis/ghidra/data"
export PATH="$GHIDRA_HOME/support:$JAVA_HOME/bin:$PATH"
unset th04_repo_root
